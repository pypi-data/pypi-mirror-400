import functools
from typing import Callable, Dict, List, Literal, Optional, Any, Union, Coroutine
from dataclasses import dataclass

from hero_base import State
from hero_base.tool import ToolResult

type HookName = Literal["tool_result", "before_reason"]

# Hook函数类型：可以是同步函数，也可以是异步函数
HookFunc = Union[
    Callable[[State, Any], Optional[ToolResult]],
    Callable[[State, Any], Coroutine[Any, Any, Optional[ToolResult]]]
]


@dataclass
class ToolHook:
    """工具调用结果的hook数据"""
    tool: str
    result: ToolResult


class HookManager:
    """Hook管理器，用于在特定时机拦截并修改结果"""
    
    def __init__(self):
        self._hooks: Dict[str, List[HookFunc]] = {}
    
    def add_hook(self, hook_name: str, hook_func: HookFunc):
        """
        添加hook函数
        
        Args:
            hook_name: hook名称，例如 "tool_result"
            hook_func: hook函数，接收 (state, hook_data) 参数，返回 ToolResult 或 None
                      - 返回 ToolResult: 使用返回的结果替换原始结果
                      - 返回 None: 保持原始结果不变
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(hook_func)
    
    async def apply_hooks(self, hook_name: str, state: State, hook_data: Any) -> Optional[ToolResult]:
        """
        应用所有注册的hook函数
        
        Args:
            hook_name: hook名称
            state: 状态对象
            hook_data: hook数据（例如 ToolHook）
        
        Returns:
            如果hook返回了新的ToolResult，则返回该结果；否则返回None表示保持原结果
        """
        if hook_name not in self._hooks:
            return None
        
        result = None
        for hook_func in self._hooks[hook_name]:
            hook_result = hook_func(state, hook_data)
            # 支持异步hook函数
            if hasattr(hook_result, '__await__'):
                hook_result = await hook_result
            
            # 如果hook返回了结果，使用它（后面的hook会覆盖前面的）
            if hook_result is not None:
                result = hook_result
        
        return result
    
    def __call__(self, *hook_name: HookName):
        """
        Hook装饰器
        
        Args:
            hook_name: hook名称，例如 "tool_result"
        
        Usage:
            @task.hook("tool_result")
            async def tool_result_hook(state: State, tool_hook: ToolHook) -> Optional[ToolResult]:
                # 可以在这里处理工具调用结果
                # 返回新的ToolResult来替换原结果，或返回None保持原结果
                import asyncio
                from hero_base.tool import ToolSuccess
                
                # 模拟异步处理
                await asyncio.sleep(1)
                
                if tool_hook.tool == "some_tool":
                    return ToolSuccess(content="修改后的结果")
                return None  # 保持原结果不变
        """
        def decorator(func: HookFunc):
            for name in hook_name:
                self.add_hook(name, func)
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
