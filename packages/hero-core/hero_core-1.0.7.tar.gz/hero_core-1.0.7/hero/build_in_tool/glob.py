import json
import os
import glob as glob_module
from typing import Optional
from pydantic import BaseModel, Field
from hero_base import State, Tool, ToolError, ToolSuccess

tool = Tool()

class Params(BaseModel):
    """
    Fast file pattern matching tool.
    Supports glob patterns like "**/*.js" or "src/**/*.ts"
    Returns matching file paths sorted by modification time
    
    Use this tool when you need to find files by name patterns
    """
    pattern: str = Field(description="The glob pattern to match files against")
    path: Optional[str] = Field(description="""The directory to search in. If not specified, the current working
directory will be used. IMPORTANT: Omit this field to use the default
directory. DO NOT enter "undefined" or "null" - simply omit it for the
default behavior. Must be a valid directory path if provided.""")

@tool(params=Params)
async def glob(pattern: str, path: Optional[str], state: State):
    working_dir = state.working_dir
    try:
        # 如果没有指定路径，使用当前工作目录
        if path is None:
            path = "."

        path = os.path.join(working_dir, path)
        
        # 检查路径是否存在
        if not os.path.exists(path):
            return ToolError(f"Path {path} does not exist")
        
        # 检查是否为目录
        if not os.path.isdir(path):
            return ToolError(f"Path {path} is not a directory")
        
        # 构建完整的搜索模式
        if not pattern.startswith('/'):
            # 如果模式不是绝对路径且不是递归模式，则相对于指定路径
            search_pattern = os.path.join(path, pattern)
        else:
            # 如果是绝对路径或递归模式，直接使用
            search_pattern = pattern
        
        # 使用 glob 模块进行模式匹配
        # 使用 recursive=True 支持 ** 递归模式
        matching_files = glob_module.glob(search_pattern, recursive=True)
        
        # 过滤掉目录，只保留文件
        files_only = []
        for file_path in matching_files:
            if os.path.isfile(file_path):
                files_only.append(file_path)
        
        # 按修改时间排序（最新的在前）
        files_only.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # 获取相对路径（相对于搜索目录）
        relative_files = []
        for file_path in files_only:
            try:
                rel_path = os.path.relpath(file_path, path)
                relative_files.append(rel_path)
            except ValueError:
                # 如果无法计算相对路径，使用绝对路径
                relative_files.append(file_path)
        
        return ToolSuccess(f"""Files: {json.dumps(relative_files, indent=4)}
Count: {len(relative_files)}""")
        
    except Exception as e:
        return ToolError(str(e))
    