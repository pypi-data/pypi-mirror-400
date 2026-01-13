import json
import os
import fnmatch
from typing import List, Optional
from pydantic import BaseModel, Field
from hero_base import State, Tool, ToolError, ToolSuccess, ToolFailed

tool = Tool()

class Params(BaseModel):
    """
    Lists files and directories in a given path. You can optionally provide an array of
    glob patterns to ignore with the ignore parameter. You should generally prefer
    the Glob tools, if you know which directories to search.
    """
    path: str = Field(description="The relative path to the directory to list. check the current working directory, set it to an empty string.")
    ignore: Optional[List[str]] = Field(description="The glob patterns to ignore.", default=[])

@tool(params=Params)
async def ls(path: str, ignore: Optional[List[str]], state: State):
    
    working_dir = state.working_dir
    try:
        if ignore is None:
            ignore = []
        
        # 如果路径为空字符串，使用当前工作目录
        if not path:
            path = "."

        path = os.path.join(working_dir, path)
        
        # 检查路径是否存在
        if not os.path.exists(path):
            return ToolError(f"Path {path} does not exist")
        
        # 检查是否为目录
        if not os.path.isdir(path):
            return ToolError(f"Path {path} is not a directory")
        
        # 获取目录内容
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            # 检查是否应该忽略此项目
            should_ignore = False
            for pattern in ignore:
                if fnmatch.fnmatch(item, pattern):
                    should_ignore = True
                    break
            
            if should_ignore:
                continue
            
            # 获取文件/目录信息
            stat_info = os.stat(item_path)
            is_dir = os.path.isdir(item_path)
            
            items.append({
                "name": item,
                "type": "directory" if is_dir else "file",
                "size": stat_info.st_size,
                "modified": stat_info.st_mtime
            })
        
        # 按名称排序
        items.sort(key=lambda x: x["name"])
        
        return ToolSuccess(f"""Items: \n{json.dumps(items, indent=4)}
Count: \n{len(items)}""")   
        
    except Exception as e:
        return ToolError(str(e))