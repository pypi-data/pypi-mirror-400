import os
from typing import List, TypedDict
from pydantic import BaseModel, Field
import traceback
from hero_base import State, Tool, ToolError, ToolSuccess
from hero.build_in_model.model import Model
from hero.util import log, function
from hero.util.tokenizer import token_count

tool = Tool()
class ReadFileOptions(TypedDict):
    content_limit: int
    model: Model

class Params(BaseModel):
    """
    Read a file
    """
    read_file_list: List[str] = Field(description="The file list to read, you should read multiple files to get the complete context and increase the efficiency, only support **TEXT and IMAGE FILES** like: txt, json, csv, md, py, js, html, png, jpg, jpeg, gif, webp, bmp, tiff, etc.")


@tool(
    params=Params,
    tool_tips=["You can use the `read_file` tool to read the file content as context, so you should try to read more files at one time to get the complete context and increase the efficiency."],
    options={
        "content_limit": -1,
        "model": Model("model", "", "")
    },
    options_type=ReadFileOptions
)
async def read_file(read_file_list: List[str], options: ReadFileOptions, state: State):
    try:
        content_limit = options["content_limit"]
        if content_limit == -1:
            content_limit = int(options["model"].context_length * 0.4)

        if not read_file_list:
            raise ValueError("Missing required parameter: read_file_list")

        working_dir = state.working_dir

        file_content = ""

        images = []
        # 验证文件列表
        for file in read_file_list:
            file_path = os.path.join(working_dir or "", file)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file}")

            if file.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff")):
                images.append(file_path)
            else:
                file_content += f'<read_file name="{file}">\n'
                # 读取文件内容
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content += file.read() + "\n"
                    try:
                        if token_count(file_content) > content_limit:
                            filename = os.path.basename(file_path)
                            return ToolError(
                                f"The file {filename} content is too long, please use `extract_key_info_from_file` tool to extract the key information."
                            )
                    except Exception as e:
                        log.error(f"Error counting tokens: {e}")
                        return ToolError(f"Error counting tokens: {e}")
                file_content += f"</read_file>\n\n"
                
        function.write_file(state.log_dir, f"read_file_context_{state.index}.md", file_content + "\n" + "\n".join(images))

        return ToolSuccess(file_content, additional_images=images)
    except Exception as e:
        log.error(f"Read file error: {e}")
        log.error(traceback.format_exc())
        return ToolError(str(e))
