from typing import List, TypedDict
from hero_base import ContentChunk, InputItem, ReasoningChunk, State, Tool, ToolError, ToolFailed, ToolSuccess, BasicModel
from pydantic import BaseModel, Field
from hero.build_in_model import Model
from hero.util import log, function
from .util import read_default_tool_prompt
import os
import re
import sys
import platform

tool = Tool()


class ProgramOptions(TypedDict):
    coder: BasicModel
    environment: str


class Params(BaseModel):
    """
    Through programming, accomplish tasks like data processing, mathematical calculations, chart drawing, encoding/decoding, website building, and user demand implementation. The programming languages available include Python, shell (bash), HTML, CSS, JavaScript, TypeScript, Node.js, etc.
    """
    demand: str = Field(
        description="The detailed requirement to be accomplished through programming, the requirement must be something the program can complete independently without the user making additional modifications or providing extra information. The key information in the user's question or task history should be directly reflected in the requirement.",
        examples=["Write a Python program to calculate the sum of two numbers"]
    )
    output_files: List[str] = Field(
        description="The files that will be output by the program.",
    )
    reference_file_list: List[str] = Field(
        description="Read some files as programming references, do not place large data files here.",
    )


@tool(
    params=Params,
    tool_tips=["You should use program tool to write each code to solve the problem.",
               "When handling data files such as csv, json, excel, sql, pdb, etc., do **not** use the `extract_key_info_from_file` tool. Instead, use the `program` tool and process via programming.",
               "If you want to use `program` tool to optimize the code, your demand should be write a new code file based on the current code file. You can use v1,v2..vn to indicate the version of the code file."],
    options={
        "coder": Model("model", "", ""),
        "environment": "",
    },
    options_type=ProgramOptions
)
async def program(demand: str, reference_file_list: List[str], options: ProgramOptions, state: State):

    content_cache = ""

    is_output_file = False
    output_file_path = ""
    output_file_name = ""
    output_files = []

    try:
        if not demand:
            yield ToolFailed("demand is required")

        if not reference_file_list:
            reference_file_list = []

        images = []
        reference_file_content = ""

        working_dir = state.working_dir

        # 数组去重
        reference_file_list = list(set(reference_file_list))

        for file_name in reference_file_list:
            extension = os.path.splitext(file_name)[1].lower()

            file_path = os.path.join(working_dir, file_name)
            if not os.path.exists(file_path):
                log.error(f"File {file_name} does not exist")
                continue

            log.debug(f"REFERENCE FILE: {file_name}")

            reference_file_content += f"<file name=\"{file_name}\">\n"
            reference_file_content += function.read_file(
                working_dir, file_name)
            reference_file_content += "\n</file>\n"

        environment = f'- OS: {platform.system()} {platform.release()}\n- Local supported fonts: "Arial Unicode MS", "sans-serif"\n'
        environment += f"- Python version: {sys.version}\n"
        if options["environment"]:
            environment += f"- {options['environment']}\n"

        # 如果有GPU信息，则添加到环境变量中
        if os.environ.get("CUDA_VISIBLE_DEVICES"):
            environment += f"- GPU: {os.environ.get('CUDA_VISIBLE_DEVICES')}\n"

        log.debug(f"environment: {environment}")

        full_demand = f"""Please generate the code file.
The files that you should output: {output_files}
Demand: {demand}"""

        user_prompt = [
            *[InputItem(type="image", value=image) for image in images],
            InputItem(type="text", value=full_demand),
        ]
        system_prompt = read_default_tool_prompt("coder.md", params={
            "environment": environment,
            "reference_file": reference_file_content,
            "user_message": state.get_user_question(),
        })

        async for chunk in options["coder"].generate(
            input=user_prompt,
            system=system_prompt,
        ):
            yield chunk
            if isinstance(chunk, ContentChunk):
                content_cache += chunk.content

        state.set_storage("program_llm_input_user_part", user_prompt)
        state.set_storage("program_llm_input_system_part", system_prompt)
        state.set_storage("program_llm_output", content_cache)

        files_content = ""
        for line in content_cache.split("\n"):
            # 处理代码文件
            if re.search(
                r"<code_file\s+file=\"(.*?)\">", line
            ):
                match = re.search(
                    r"<code_file\s+file=\"(.*?)\">", line
                )
                if match:
                    output_file_name = match.group(1)
                files_content += f"<code_file name=\"{output_file_name}\">\n"
                output_file_path = os.path.join(working_dir, output_file_name)

                # 如果文件存在，则把现有文件改名
                if os.path.exists(output_file_path):
                    # 获取当前时间
                    timestamp = function.timestamp()
                    # 改名
                    os.rename(
                        output_file_path,
                        os.path.join(
                            working_dir, f"__{output_file_name}_{timestamp}.py"
                        ),
                    )

                # 新建空文件
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write("")

                # 设置标志位，后续将 line 写入文件
                is_output_file = True

                # 清空 line，特殊标志不输出，原始内容debug打印出来
                line = None

            elif "</code_file>" in line:
                is_output_file = False
                output_file_name = ""
                output_file_path = ""
                line = None
                files_content += "\n</code_file>\n"

            if not line == None:
                if is_output_file:
                    if output_file_path not in output_files:
                        output_files.append(output_file_path)
                    with open(output_file_path, "a", encoding="utf-8") as f:
                        f.write(line + "\n")
                    files_content += line + "\n"

        state.set_storage("program_output_files", output_files)

        yield ToolSuccess(files_content)

    except Exception as e:
        yield ToolError(str(e))
