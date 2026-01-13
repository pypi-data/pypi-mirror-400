import traceback
from pydantic import BaseModel, Field
from hero.util import log, function
from hero_base import State, Tool, ToolError, ToolSuccess

tool = Tool()


class Params(BaseModel):
    """
    Make a experiment report.
    """

    objective: str = Field(description="The objective of the experiment.")
    theoretical_background: str = Field(
        description="The theoretical background of the experiment."
    )
    method: str = Field(description="The method of the experiment.")
    result: str = Field(description="The result of the experiment.")
    analysis: str = Field(description="The analysis of the experiment.")
    conclusion: str = Field(description="The conclusion of the experiment.")

    write_file: str = Field(
        description="The name of the file to write the experiment report to (append mode, not overwrite)."
    )


@tool(
    params=Params,
    tool_tips=[
        "After you finish a experiment (Like conducted a programming session, a deep research project, data analysis, and reading, etc.), you should use the `experiment_report` tool to make a experiment report.",
    ],
)
async def experiment_report(
    objective: str,
    theoretical_background: str,
    method: str,
    result: str,
    analysis: str,
    conclusion: str,
    write_file: str,
    state: State,
):
    try:
        if not objective:
            raise ValueError("Missing required parameter: objective")
        if not theoretical_background:
            raise ValueError("Missing required parameter: theoretical_background")
        if not method:
            raise ValueError("Missing required parameter: method")
        if not result:
            raise ValueError("Missing required parameter: result")
        if not analysis:
            raise ValueError("Missing required parameter: analysis")
        if not conclusion:
            raise ValueError("Missing required parameter: conclusion")
        if not write_file:
            raise ValueError("Missing required parameter: write_file")

        log.debug(f"experiment_report: {objective}")
        log.debug(f"experiment_report: {theoretical_background}")
        log.debug(f"experiment_report: {method}")
        log.debug(f"experiment_report: {result}")
        log.debug(f"experiment_report: {analysis}")
        log.debug(f"experiment_report: {conclusion}")
        log.debug(f"experiment_report: {write_file}")

        note = f"<experiment_report>\n"
        note += f"objective: {objective}\n\n"
        note += f"theoretical_background: {theoretical_background}\n\n"
        note += f"method: {method}\n\n"
        note += f"result: {result}\n\n"
        note += f"analysis: {analysis}\n\n"
        note += f"conclusion: {conclusion}\n"
        note += f"</experiment_report>\n\n"

        function.append_file(state.working_dir, write_file, note)

        return ToolSuccess(f"Experiment report written to {write_file}")

    except Exception as e:
        log.error(f"experiment_report error: {e}")
        log.error(traceback.format_exc())
        return ToolError(str(e))
