from pydantic import BaseModel, Field
from hero_base import State, Tool, ToolFailed, ToolSuccess
from hero.util import function

tool = Tool()
class Params(BaseModel):
    """
    Analyze the current situation and difficulties, reflect on the past, and brainstorm the improvements or big changes. The make a new plan.
    """
    current_situation: str = Field(description="The current situation.")
    difficulties: str = Field(description="The difficulties.")
    reflection: str = Field(description="The reflection.")
    brainstorm: str = Field(description="The brainstorm.")
    new_plan: str = Field(description="The new plan.")
    write_file: str = Field(description="The name of the file to write. like brainstorm.md.")

@tool(
    params=Params,
    tool_tips=["You should use the `reflect_and_brainstorm` tool frequently, especially when you encounter difficulties or your progress stalls, to make a brainstorming and try to find a new way to solve the problem."],
)
async def reflect_and_brainstorm(current_situation: str, difficulties: str, reflection: str, brainstorm: str, new_plan: str, write_file: str, state: State):
    if not current_situation:
        return ToolFailed(content="The current situation is required.")
    if not difficulties:
        return ToolFailed(content="The difficulties are required.")
    if not reflection:
        return ToolFailed(content="The reflection is required.")
    if not brainstorm:
        return ToolFailed(content="The brainstorm is required.")
    if not new_plan:
        return ToolFailed(content="The new plan is required.")
    if not write_file:
        return ToolFailed(content="The name of the file to write is required.")
    function.write_file(state.working_dir, write_file, f"current_situation: {current_situation}\n\ndifficulties: {difficulties}\n\nreflection: {reflection}\n\nbrainstorm: {brainstorm}\n\nnew_plan: {new_plan}")
    return ToolSuccess(f"The new plan has been written to the file {write_file}")