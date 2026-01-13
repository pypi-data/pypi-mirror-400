import traceback
from pydantic import BaseModel, Field
from hero.util import log, function
from hero_base import State, Tool, ToolError, ToolSuccess

tool = Tool()


class Params(BaseModel):
    """
    Record the key assumptions, thoughts, reflections, improvements, analysis, information, key details into a file (append mode, not overwrite) and `task_execute_history` for later reference during subsequent tasks.
    """

    note: str = Field(
        description="The key assumptions, thoughts, reflections, improvements, analysis, information, key details."
    )
    write_file: str = Field(description="The name of the file to append the note to.")


@tool(
    params=Params,
    tool_tips=[
        "When you need to stop and think, you should use the `write_a_note` tool to record you thoughts, reflections, or any other key information.",
    ],
)
async def write_a_note(note: str, write_file: str, state: State):
    try:
        if not note:
            raise ValueError("Missing required parameter: note")
        if not write_file:
            raise ValueError("Missing required parameter: write_file")

        log.debug(f"write_a_note: {note}")
        log.debug(f"write_a_note: {write_file}")

        note = f"<note>\n{note}\n</note>\n\n"

        function.append_file(state.working_dir, write_file, note)

        return ToolSuccess(f"Note appended to {write_file}")

    except Exception as e:
        log.error(f"write_a_note error: {e}")
        log.error(traceback.format_exc())
        return ToolError(str(e))
