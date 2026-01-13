import json
from typing import List, TypedDict
from hero_base import ContentChunk, ReasoningChunk, Tool, ToolEnd, State, BasicModel, ToolFailed
from hero.build_in_model import Model
from pydantic import BaseModel, Field
from os import path


class Params(BaseModel):
    """
    If you believe that you have sufficient and accurate information to answer the user's question, please invoke the `final_answer` tool.**Don't call the `final_answer` tool until you reach the goal.**
    """
    answer: str = Field(description="The final answer")
    file_list: List[str] = Field(
        description="When the user's question corresponds to content such as code files, analysis reports, etc., fill it into this array; otherwise, leave it empty.")


tool = Tool()


class FinalAnswerOption(TypedDict):
    model: BasicModel


@tool(params=Params,
      tool_tips=["You should use the `final_answer` tool to give the final answer and stop the task."],
      options={
          "model": Model("model", "", ""),
      }, options_type=FinalAnswerOption
      )
async def final_answer(answer: str, file_list: List[str], options: FinalAnswerOption, state: State):
    question = state.get_user_question()

    eval_prompt = f"""
    You are given a question and a final answer.
    You need to assess whether the answer can truly solve the problem, considering aspects such as relevance, feasibility, completeness, and other characteristics.
    you need return a json object with the following fields:
    - truly_solve: true or false
    - reason: Provide your thoughts on why you think the problem can be successfully solved, or why the answer cannot resolve the issue.
    example:
    {{
        "truly_solve": true,
        "reason": "The answer is relevant to the question, complete and feasible."
    }}
    The question is: {question}
    The final answer is: {answer}
    """

    for file in file_list:
        if not path.exists(path.join(state.working_dir, file)):
            continue
        content = open(path.join(state.working_dir, file),
                       "r", encoding="utf-8").read()
        eval_prompt += f"""
        The file {file} content is: {content}
        """

    eval_content = ""  # 初始化 eval_content 变量
    async for chunk in options["model"].generate(
        input=eval_prompt,
        response_format={
            "type": "json_object",
        }
    ):
        if isinstance(chunk, ContentChunk | ReasoningChunk):
            yield chunk.content
        if isinstance(chunk, ContentChunk):
            eval_content += chunk.content

    # 检查 eval_content 是否为空
    if not eval_content.strip():
        yield ToolFailed("Can't get the eval result, the model response is empty.")

    try:
        if "```json" in eval_content:
            # 从前找到第一个 ```json 的index
            json_index = eval_content.find("```json")
            eval_content = eval_content[json_index + 7:]
            # 从后找到第一个 ``` 的index
            last_json_index = eval_content.rfind("```")
            eval_content = eval_content[:last_json_index]
        eval_result = json.loads(eval_content)
    except json.JSONDecodeError as e:
        yield ToolFailed(f"Parse the eval result failed: {e}")

    if eval_result.get("truly_solve", False):
        yield ToolEnd(f"{answer}", file_list)
    else:
        reason = eval_result.get("reason", "")
        yield ToolFailed(f"the answer is not truly solve the problem, reason: {reason}")
