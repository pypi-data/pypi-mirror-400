import os
from pydantic import BaseModel, Field
from hero_base import State, Tool, ToolError, ToolSuccess

tool = Tool()

class Params(BaseModel):
    """
    Performs exact string replacements in files.

    Usage:

    - You must use your `Read` tool at least once in the conversation before
    editing. This tool will error if you attempt an edit without reading the file.

    - When editing text from Read tool output, ensure you preserve the exact
    indentation (tabs/spaces) as it appears AFTER the line number prefix. The line
    number prefix format is: spaces + line number + tab. Everything after that tab
    is the actual file content to match. Never include any part of the line number
    prefix in the old_string or new_string.

    - ALWAYS prefer editing existing files in the codebase. NEVER write new files
    unless explicitly required.

    - Only use emojis if the user explicitly requests it. Avoid adding emojis to
    files unless asked.

    - The edit will FAIL if `old_string` is not unique in the file. Either provide
    a larger string with more surrounding context to make it unique or use
    `replace_all` to change every instance of `old_string`.

    - Use `replace_all` for replacing and renaming strings across the file. This
    parameter is useful if you want to rename a variable for instance.
    """
    file_path: str = Field(description="The relative path to the file to modify (like file.txt or dir/file.txt)")
    old_string: str = Field(description="The text to replace")
    new_string: str = Field(description="The text to replace it with (must be different from old_string)")
    replace_all: bool = Field(description="Replace all occurences of old_string (default false)", default=False)

@tool(
    params=Params,
)
async def edit(file_path: str, old_string: str, new_string: str, replace_all: bool, state: State):
    try:
        working_dir = state.working_dir
        
        # 验证参数
        if not file_path:
            return ToolError("File path cannot be empty")
        
        if not old_string:
            return ToolError("Old string cannot be empty")
        
        if old_string == new_string:
            return ToolError("Old string and new string cannot be the same")
        
        # 构建完整文件路径
        full_file_path = os.path.join(working_dir or "", file_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_file_path):
            return ToolError(f"File not found: {full_file_path}")
        
        # 检查是否为文件（不是目录）
        if not os.path.isfile(full_file_path):
            return ToolError(f"Path is not a file: {full_file_path}")
        
        # 读取文件内容
        try:
            with open(full_file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            return ToolError(f"Cannot read file {full_file_path}: file is not text encoded")
        except Exception as e:
            return ToolError(f"Error reading file {full_file_path}: {str(e)}")
        
        # 检查old_string是否存在于文件中
        if old_string not in content:
            return ToolError(f"String '{old_string}' not found in file {full_file_path}")
        
        # 检查old_string是否唯一（当replace_all为False时）
        if not replace_all:
            count = content.count(old_string)
            if count > 1:
                return ToolError(f"String '{old_string}' appears {count} times in file. Use replace_all=True to replace all occurrences, or provide more context to make the string unique.")
        
        # 执行替换
        if replace_all:
            new_content = content.replace(old_string, new_string)
            replacement_count = content.count(old_string)
        else:
            new_content = content.replace(old_string, new_string, 1)
            replacement_count = 1
        
        # 检查是否有实际变化
        if new_content == content:
            return ToolError("No changes made to the file")
        
        # 写入文件
        try:
            with open(full_file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            return ToolError(f"Error writing to file {full_file_path}: {str(e)}")
        
        return ToolSuccess(f"File {full_file_path} edited successfully. Replaced {replacement_count} occurrence(s).")
        
    except Exception as e:
        return ToolError(str(e))
