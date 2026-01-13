import os
import subprocess
from typing import Optional
from pydantic import BaseModel, Field
from hero_base import State, Tool, ToolError, ToolSuccess

tool = Tool()


class Params(BaseModel):
    """
    A powerful search tool built on ripgrep

    Usage:
    - ALWAYS use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command. The Grep tool has been optimized for correct permissions and access.
    - Supports full regex syntax (e.g., "log.*Error", "function\s+\w+")
    - Filter files with glob parameter (e.g., "*.js", "**/*.tsx") or type parameter (e.g., "js", "py", "rust")
    - Output modes: "content" shows matching lines, "files_with_matches" shows only file paths (default), "count" shows match counts
    - Use Task tool for open-ended searches requiring multiple rounds
    - Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping (use `interface\{\}` to find `interface{}` in Go code)
    - Multiline matching: By default patterns match within single lines only. For cross-line patterns like `struct \{[\s\S]*?field`, use `multiline: true`
    """
    pattern: str = Field(
        description="The regular expression pattern to search for in file contents")
    path: Optional[str] = Field(
        description="File or directory to search in (rg PATH). Defaults to current working directory.", default=None)
    glob: Optional[str] = Field(
        description="Glob pattern to filter files (e.g. '*.js', '*.{ts,tsx}') - maps to rg --glob", default=None)
    output_mode: str = Field(
        description="Output mode: 'content' shows matching lines, 'files_with_matches' shows file paths, 'count' shows match counts. Defaults to 'files_with_matches'.", default="files_with_matches")
    before_lines: Optional[int] = Field(
        description="Number of lines to show before each match (rg -B). Requires output_mode: 'content', ignored otherwise.", default=None)
    after_lines: Optional[int] = Field(
        description="Number of lines to show after each match (rg -A). Requires output_mode: 'content', ignored otherwise.", default=None)
    context_lines: Optional[int] = Field(
        description="Number of lines to show before and after each match (rg -C). Requires output_mode: 'content', ignored otherwise.", default=None)
    show_line_numbers: Optional[bool] = Field(
        description="Show line numbers in output (rg -n). Requires output_mode: 'content', ignored otherwise.", default=False)
    case_insensitive: Optional[bool] = Field(
        description="Case insensitive search (rg -i)", default=False)
    type: Optional[str] = Field(
        description="File type to search (rg --type). Common types: js, py, rust, go, java, etc. More efficient than include for standard file types.", default=None)
    head_limit: Optional[int] = Field(
        description="Limit output to first N lines/entries, equivalent to '| head -N'. Works across all output modes: content (limits output lines), files_with_matches (limits file paths), count (limits count entries). When unspecified, shows all results from ripgrep.", default=None)
    multiline: Optional[bool] = Field(
        description="Enable multiline mode where . matches newlines and patterns can span lines (rg -U --multiline-dotall). Default: false.", default=False)


@tool(params=Params)
async def grep(
    pattern: str, path: Optional[str], glob: Optional[str], output_mode: str,
    before_lines: Optional[int], after_lines: Optional[int], context_lines: Optional[int],
    show_line_numbers: Optional[bool], case_insensitive: Optional[bool], type: Optional[str],
    head_limit: Optional[int], multiline: Optional[bool], state: State
):
    working_dir = state.working_dir
    try:
        # 构建 ripgrep 命令
        cmd = ["rg"]

        # 添加输出模式相关参数
        if output_mode == "count":
            cmd.append("--count")
        elif output_mode == "files_with_matches":
            cmd.append("--files-with-matches")
        else:  # content mode
            if show_line_numbers:
                cmd.append("-n")
            if before_lines is not None:
                cmd.extend(["-B", str(before_lines)])
            if after_lines is not None:
                cmd.extend(["-A", str(after_lines)])
            if context_lines is not None:
                cmd.extend(["-C", str(context_lines)])

        # 添加其他参数
        if case_insensitive:
            cmd.append("-i")
        if multiline:
            cmd.append("-U")
        if glob:
            cmd.extend(["--glob", glob])
        if type:
            cmd.extend(["--type", type])

        # 添加搜索路径
        if path:
            search_path = os.path.join(working_dir, path)
        else:
            search_path = working_dir

        # 添加模式和路径
        cmd.append(pattern)
        cmd.append(search_path)

        # 执行命令
        result = subprocess.run(cmd, capture_output=True,
                                text=True, cwd=working_dir)

        if result.returncode == 0:
            output = result.stdout.strip()

            # 应用 head_limit 如果指定
            if head_limit and output:
                lines = output.split('\n')
                if len(lines) > head_limit:
                    output = '\n'.join(lines[:head_limit])

            return ToolSuccess(output)
        elif result.returncode == 1:
            # ripgrep 返回 1 表示没有找到匹配项
            return ToolSuccess("No matches found")
        else:
            # 其他错误
            return ToolError(f"ripgrep error: {result.stderr}")

    except FileNotFoundError:
        return ToolError("ripgrep not found. Please install ripgrep (rg) to use this tool.")
    except Exception as e:
        return ToolError(f"Error executing grep: {str(e)}")
