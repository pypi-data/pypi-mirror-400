import sys
from typing import List, TypedDict
from hero_base import State, Tool, ToolError, ToolSuccess
from pydantic import BaseModel, Field
from hero.util import function
from hero.util.shell import shell_util
import re

tool = Tool()


class Params(BaseModel):
    """
    Execute shell commands to complete tasks.
    """
    command_list: List[str] = Field(
        description="The shell command list to execute.")


class ShellOptions(TypedDict):
    timeout: int


@tool(Params,
      tool_tips=["Shell commands must include a timeout error or an auto-termination mechanism, should not be allowed to run indefinitely."],
      options={
          "timeout": sys.maxsize,
      },
      options_type=ShellOptions)
async def execute_shell(command_list: List[str], options: ShellOptions, state: State):
    timeout = options["timeout"]
    if not command_list:
        return ToolError("No command list provided.")

    message_list = []

    for command in command_list:
        try:
            # 执行命令
            command = re.sub(r"#.*\n?", "", command).strip()
            if not command:
                continue

            stdout, stderr = await shell_util(command, state, timeout)
            if not stdout or not stderr:
                message = f'<shell command="{command}">\n'
                message += f"## Stdout:\n"
                message += f"{function.get_head_and_tail_n_chars(stdout)}\n"
                message += f"## Stderr:\n"
                message += f"{function.get_head_and_tail_n_chars(stderr)}\n"
                message += f"</shell>\n"

            message_list.append(message)

            if stderr:
                return ToolError("\n\n".join(message_list))

        except Exception as e:
            message_list.append(f"<error>\n\n{str(e)}\n\n</error>\n\n")
            return ToolError(str(e))

    return ToolSuccess("\n\n".join(message_list))
