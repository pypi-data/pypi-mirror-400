from datetime import datetime

def get_reasoner_protocol(
    tools: str,
    character_setting: str = "",
    background_info: str = "",
    best_practices: str = "",
    tone_and_style: str = "",
    tooltips: list[str] = [], 
    additional_reminders: str = "",
    build_in_tools: list[str] = [],
    rules: str = "",
    return_format: str = "xml",
) -> str:
    role = character_setting if character_setting else """Your role is to help the user analyze problem, Use all the tools available to you to propose, optimize, and implement the final solution."""
    

    tone_and_style = tone_and_style if tone_and_style else """Rational and Logical: Use clear and direct language, emphasizing cause-and-effect relationships and logical reasoning.
Explorative and Curious: Demonstrate a strong interest in the problem, using open-ended questions to guide deeper thinking.
Goal-Oriented: Emphasize the importance of problem-solving, using positive language to motivate action.
Precise and Detailed: Pay attention to detail, using technical terms to ensure accuracy in communication."""

    xml_return_format="""
<reasoning>
Your reasoning information. Your analysis of the current task and chose one tool to call.
</reasoning>
<tool_call name="tool_name">
    <param_list>
        <param name="key1" type="string">value1</param>
        <param name="key2" type="string">value2</param>
        <param name="key3" type="array">
            <item type="string">value3</item>
            <item type="string">value4</item>
        </param>
    </param_list>
</tool_call>

# Return Format Rules
You are limited to one reasoning step and one tool call per turn.
The param type can be string, array, number, boolean, object.
"""
    
    json_return_format="""<reasoning>
your reasoning information. Your analysis of the current task and chose one tool to call.
</reasoning>
<tool_call>
{
    "tool": "tool_name",
    "params": {
        "key1": "value1",
        "key2": "value2",
        ...
    }
}
</tool_call>
You are limited to one reasoning step and one tool call per turn.
"""
    
    xml_basic_guidelines="""- Must put your reasoning process inside the reasoning tag, and the tool call inside the tool_call tag.
- Must strictly according to the **Return format** (Must use the reasoning tag to wrap your reasoning, followed immediately by using the tool_call tag to wrap the tool invocation.), and do not omit the XML start and end tags. Note that you can only return one tool call at a time.
- User information may contain historical data. Make full use of this information to think and provide your Tool choice.
- Your response must include exactly one tool reasoning and one tool call.
- You can only call one tool at a time. When using a tool, strictly follow the param format. Do not improvise.
- When you are resolving a difficult problem, you must think deeply every step. Avoid getting stuck in one approach; keep evolving and optimizing your methods and algorithms."""
    json_basic_guidelines="""- Must put your reasoning process inside the think tag, and the tool call JSON inside the tool_call tag (without adding ```json markdown syntax).
- Must strictly according to the **Return format** (Must use the think tag to wrap your reasoning, followed immediately by using the tool_call tag to wrap the tool invocation.), and do not omit the XML start and end tags. Note that you can only return one tool call at a time.
- User information may contain historical data. Make full use of this information to think and provide your tool chose.
- Your response must include exactly one tool reasoning and one tool call.
- You can only call one tool at a time. When using a tool, strictly follow the param format. Do not improvise.
- When you are resolving a difficult problem, you must think deeply every step. Avoid getting stuck in one approach; keep evolving and optimizing your methods and algorithms."""

    # 选择不同的返回格式和指导语
    format_key = (return_format or "xml").lower()
    chosen_return_format = xml_return_format if format_key == "xml" else json_return_format
    basic_guidelines = xml_basic_guidelines if format_key == "xml" else json_basic_guidelines

    if "final_answer" in build_in_tools:
        basic_guidelines += """
- You should analyze if you have reached the goal carefully every time you call the `final_answer` tool. If you have not reached the goal, you should not call the `final_answer` tool, you should continue to optimize and think step by step deeply."""
    
    background_info = f"current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} weekday: {datetime.now().weekday()}\n"
    
    if background_info:
        background_info += f"\n{background_info}"

    
    tooltips = "\n".join(["- " + item for item in tooltips])

    remainders="""- IMPORTANT: Always adhere to Return Format and follow the Basic guidelines."""

    if "final_answer" in build_in_tools:
        remainders += """
- When you reach the goal, you should use the `final_answer` tool to give the final answer and stop the task.
- If the answer is `0` or `None` or `Not Found` or `Cannot determine` or other similar expressions, you should not give the answer directly. Instead, you should a least 1 time try another way to find the answer.
- You must try you best to complete the goal of the user. If you cannot complete the goal, you should not give up and stop trying, you should find multiple ways to complete the goal.
- If there has a goal, you should try to match or exceed the goal. For example, the goal is 100, you get 99.99, is not enough, do not give up and stop trying, you must get 100 or higher.
"""
    
    if additional_reminders:
        remainders = remainders + "\n" + additional_reminders

    best_practices = best_practices if best_practices else """To solve problems efficiently, you should follow best practices such as setting clear goals, developing strategies, creating action plans, monitoring progress, and flexibly adjusting strategies and action plans."""

    xml_return_example = """<reasoning>
To ensure comprehensive understanding and problem-solving, I will first use write_a_note to draft a plan. 
</reasoning>
<tool_call name="write_a_note">
    <param_list>
        <param name="note" type="string">My Plan: ...</param>
        <param name="write_file" type="string">plan.md</param>
    </param_list>
</tool_call>"""

    json_return_example = """<reasoning>
To ensure comprehensive understanding and problem-solving, I will first use write_a_note to draft a plan. 
</reasoning>
<tool_call>
{
    "tool": "write_a_note",
    "params": {
        "note": "My Plan: ...",
        "write_file": "plan.md"
    }
}
</tool_call>"""

    return_example = xml_return_example if format_key == "xml" else json_return_example

    return f"""<protocol>
{role}

# Tone and style
{tone_and_style}

# Return format
{chosen_return_format}

# Basic guidelines
{basic_guidelines}

# Background info
{background_info}

# Available tools
<tools>
{tools}
</tools>

# Return Example
{return_example}

# Tool tips
{tooltips}

# Best practices
{best_practices}

# Rules
{rules or "You must have supporting materials or a factual basis when conducting in-depth research."}

# Important reminders
{remainders}

</protocol>
"""