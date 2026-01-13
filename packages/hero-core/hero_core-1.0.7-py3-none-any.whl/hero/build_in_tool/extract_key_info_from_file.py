import os
from typing import List, TypedDict
from pydantic import BaseModel, Field
import traceback
from hero_base import State, Tool, ToolError, ToolSuccess, ContentChunk, BasicModel
from hero.build_in_model import Model
from hero.util import log, function
from .util import read_default_tool_prompt

class Params(BaseModel):
    """
    Read context from file, carefully analyze, and extract key information related to the user's question. It will then write the information to the task history and an independent file.
    """
    read_file_list: List[str] = Field(
        description="Get the file name from context, can be one or more files. Do not generate filenames yourself, do not read non-text files (e.g., .pdf/.docx/.pptx/.xlsx/.csv/.json/.yaml/.py/.js/.ts/.html/.css/.ipynb), do not read images.",
        examples=[["example1.md", "example2.txt"]]
    )
    write_file: str = Field(
        description="Write the extracted key information to a .md file",
        examples=["example.md"]
    )
    query: str = Field(
        description="Query related to the user's question and file content",
        examples=["What is the main idea of the document?"]
    )

class ExtractKeyInfoFromFile(TypedDict):
    model: BasicModel
    split_content_limit: int
    split_file_limit: int


tool = Tool()


@tool(
    params=Params,
    options={
        "model": Model("model", "", ""),
        "split_content_limit": -1,
        "split_file_limit": 5
    },
    options_type=ExtractKeyInfoFromFile)
async def extract_key_info_from_file(read_file_list: List[str], write_file: str, query: str, options: ExtractKeyInfoFromFile, state: State):
    try:
        split_content_limit = options["split_content_limit"]
        if split_content_limit == -1:
            # 40% of the model's context length
            # TODO: use tokenizer to count the tokens instead of length
            split_content_limit = int(options["model"].context_length * 0.4)

        if not read_file_list or not write_file or not query:
            raise ValueError("Missing required parameters")

        # 读取文件内容
        for file_name in read_file_list:
            file_path = os.path.join(state.working_dir, file_name)
            content = ""

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            parts = split_markdown(content, split_content_limit)
            part_length = len(parts)
            log.debug(f"Read {part_length} parts from {file_name}")

            if part_length > options["split_file_limit"]:
                raise ValueError(
                    f"File {file_name} has {part_length} parts, which is greater than the limit {options["split_file_limit"]}. This file is too large, it cannot be processed."
                )

            key_info = ""

            for index, part in enumerate(parts):
                log.debug(
                    f"Processing part {index + 1} of {part_length} from {file_name}"
                )
                log.debug(f"length: {len(part)}")

                # 使用模型提取关键信息
                user_message = str(state.get_user_question())
                log.debug(f"user_message: {user_message}")

                message = f"File: {file_name} Total: {part_length}(Parts) Current: {index + 1}(Part)\n"
                message += f"Content of Part {index + 1} has been printed below, between <content> and </content>.\n"
                message += f"Please extract the key information from the **content** strictly following the **protocal**.\n"

                key_info += (
                    f'<key_info file_name="{file_name}" part="{index + 1}">\n\n'
                )

                # 使用模型提取关键信息
                async for chunk in options["model"].generate(
                    input=message,
                    system=read_default_tool_prompt("extractor.md", params={
                        "content": part,
                        "user_message": user_message,
                        "query": query,
                    }),
                ):
                    yield chunk
                    if isinstance(chunk, ContentChunk):
                        key_info += chunk.content

                key_info += f"\n</key_info>\n"

            function.write_file(state.working_dir, write_file, key_info)

            yield ToolSuccess(f"Extract key information from {read_file_list} successfully. The key information has been written to {write_file}.")

    except Exception as e:
        log.error(f"Error in extract_key_info_from_file: {e}")
        log.error(traceback.format_exc())
        yield ToolError(str(e))


def split_markdown(content: str, limit: int) -> List[str]:
    """
    将 Markdown 内容按照标题分割，并确保每部分不超过指定长度
    """
    blocks = content.split("## ")
    temp_str = ""
    text_array = []

    for i in range(len(blocks)):
        if len(temp_str + blocks[i]) > limit:
            split_array = split_line_by_limit(temp_str, limit)
            text_array.extend(split_array)
            temp_str = ""
        temp_str += "## " + blocks[i]

    split_array = split_line_by_limit(temp_str, limit)
    text_array.extend(split_array)
    return text_array


def split_line_by_limit(text: str, limit: int) -> List[str]:
    """
    将文本按行分割，确保每一段不超过指定长度
    """
    lines = text.split("\n")
    result = []
    temp_str = ""

    for i in range(len(lines)):
        if len(temp_str) > limit:
            split_array = split_string_by_length(temp_str, limit)
            result.extend(split_array)
            temp_str = ""
        if len(temp_str + lines[i]) > limit:
            result.append(temp_str)
            temp_str = ""
        temp_str += lines[i]

    if len(temp_str) > limit:
        split_array = split_string_by_length(temp_str, limit)
        for part in split_array:
            print(len(part))
        result.extend(split_array)
    elif len(temp_str) > 0:
        result.append(temp_str)

    return result


def split_string_by_length(text: str, length: int) -> List[str]:
    """
    将字符串按指定长度分割
    """
    return [text[i: i + length] for i in range(0, len(text), length)]
