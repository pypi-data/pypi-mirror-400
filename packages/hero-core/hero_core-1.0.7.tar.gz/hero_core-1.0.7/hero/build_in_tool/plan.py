import traceback
from pydantic import BaseModel, Field
from hero.util import log, function
from hero_base import State, Tool, ToolError, ToolSuccess

tool = Tool()


class Params(BaseModel):
    """
    Make a plan for the next tasks.
    """

    objective: str = Field(description="The objective of the plan.")
    current_situation: str = Field(
        description="The content of the current situation analysis. "
    )
    new_plan: str = Field(description="The new plan for the next tasks.")
    write_file: str = Field(
        description="The name of the file to write the plan to (append mode, not overwrite)."
    )


@tool(
    params=Params,
    tool_tips=[
        "At start, you should use the `plan` tool to analyze the user message and make a useful and effective plan. After serveral tasks, you also should use the `plan` tool to review the objective and analyze the current situation and update a new plan.",
    ],
)
async def plan(
    objective: str, current_situation: str, new_plan: str, write_file: str, state: State
):
    try:
        if not objective:
            raise ValueError("Missing required parameter: objective")
        if not current_situation:
            raise ValueError("Missing required parameter: current_situation")
        if not new_plan:
            raise ValueError("Missing required parameter: new_plan")
        if not write_file:
            raise ValueError("Missing required parameter: write_file")

        log.debug(f"plan: {objective}")
        log.debug(f"plan: {current_situation}")
        log.debug(f"plan: {new_plan}")
        log.debug(f"plan: {write_file}")

        note = f"<plan>\n"
        note += f"objective: {objective}\n\n"
        note += f"current_situation: {current_situation}\n\n"
        note += f"new_plan: {new_plan}\n"
        note += f"</plan>\n\n"

        function.append_file(state.working_dir, write_file, note)

        return ToolSuccess(f"Plan written to {write_file}")

    except Exception as e:
        log.error(f"plan error: {e}")
        log.error(traceback.format_exc())
        return ToolError(str(e))
