from pydantic import BaseModel, Field
from hero.util import function
from hero_base import State, Tool, ToolError, ToolSuccess

tool = Tool()

class Params(BaseModel):
    """
    Writes a file to the local filesystem.
    Usage:

    - This tool will overwrite the existing file if there is one at the provided
    path.

    - If this is an existing file, you MUST use the Read tool first to read the
    file's contents. This tool will fail if you did not read the file first.

    - ALWAYS prefer editing existing files in the codebase. NEVER write new files
    unless explicitly required.

    - NEVER proactively create documentation files (*.md) or README files. Only
    create documentation files if explicitly requested by the User.

    - Only use emojis if the user explicitly requests it. Avoid writing emojis to
    files unless asked.
    """
    file_path: str = Field(description="The relative path to the file to write (like file.txt or dir/file.txt)")
    content: str = Field(description="The content to write to the file")

@tool(params=Params)
async def write(file_path: str, content: str, state: State):
    try:
        function.write_file(state.working_dir, file_path, content)
        return ToolSuccess(f"File {file_path} written successfully")
    except Exception as e:
        return ToolError(str(e))
