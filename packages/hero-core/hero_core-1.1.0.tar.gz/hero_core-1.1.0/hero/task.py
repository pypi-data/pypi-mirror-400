import asyncio
from dataclasses import dataclass
from enum import Enum
import inspect
import json
import os
from typing import Any, List, Literal, Optional
from hero.compressor.compressor import Compressor, CustomCompress
from hero.util.constant import TASK_ENHANCE_FILENAME, TASK_HISTORY_FILENAME
from hero_base import ReActItem, InputItem, ReasoningChunk, ToolError, UserMessageItem, State, CommonToolWrapper, ToolCallResult
from hero_base.tool import ToolEnd, ToolResult, ToolSuccess, ToolFailed
from hero.build_in_model.model import Model
from hero_base import ContentChunk
from hero_base.memory import Memory, MemoryHints
from hero.compressor.compressor import CompressedTaskHistory
from hero.util import function
from hero.event import Event, ReasonEndEvent, ReasonErrorEvent, ReasonGenerationEvent, ReasonStartEvent, StateSnapshot, TaskStartEvent, TaskEndEvent, TaskErrorEvent, ToolCallEvent, ToolFailedEvent, ToolSuccessEvent, ToolErrorEvent, ToolEndEvent, CompressStartEvent, CompressYieldEvent, CompressEndEvent, ToolYieldEvent
from hero.event import EventListener
from hero.hook import HookManager, ToolHook


class TaskStatus(Enum):
    INIT = "init"
    RUNNING = "running"
    STOP = "stop"
    ERROR = "error"
    END = "end"

@dataclass
class TaskResult:
    status: Literal["end", "interrupt", "error"]
    last_tool: str
    content: str
    additional_outputs: Optional[List[str]] = None

@dataclass
class Context:
    enhance_history: List[InputItem]
    additional_images: List[str]

class TaskBase:

    def __init__(self,
                 workspace_root: str,
                 workspace_id: str,
                 model: Model,
                 reasoner_prompt: str,
                 tools: List[CommonToolWrapper],
                 max_turn: int,
                 restart_turn: int,
                 return_format: str = "xml",
                 ) -> None:
        self.status = TaskStatus.INIT
        self.workspace_root = workspace_root
        self.workspace_id = workspace_id
        self.workspace = os.path.join(self.workspace_root, workspace_id)
        # TODO: 扩展不同的 Model 类型
        self.model = model
        self.reasoner_prompt = reasoner_prompt
        self.__tools = tools
        self.max_turn = max_turn
        self.restart_turn = restart_turn
        self.return_format = return_format
        self.user_message = ""
        self.__history: List[ReActItem | UserMessageItem] = []
        self.__context: Context = Context(
            enhance_history=[],
            additional_images=[],
        )
        self.state = State(
            workspace=self.workspace,
            history=self.__history,
            default_model=model,
        )
        self.listener = EventListener()
        self.hook = HookManager()
        hints: List[MemoryHints] = []
        for tool in self.__tools:
            if tool.memory_hint:
                hints.append(MemoryHints(
                    tool=tool.name,
                    hint=tool.memory_hint
                ))
        self.__memory: Memory = Memory(log_dir=self.state.log_dir, hints=hints)
        self.__compressor = Compressor(self.model)
        self.__reasoning: Optional[asyncio.Task[tuple[str, str, List[dict[str, Any]], str]]] = None
        self.__tool_calling: Optional[asyncio.Task[ToolResult]] = None

    # not private but protected
    async def _recover_task(self):
        history = self.__read_history()
        if not history:
            return
        last_index = len(history) - 1
        for i in range(len(history) - 1, -1, -1):
            item = history[i]
            if (isinstance(item, ReActItem) and item.tool_result) or (isinstance(item, UserMessageItem)):
                last_index = i
                break
        history = history[:last_index + 1]
        self.__set_history(history)
        for i in range(len(history) - 1, -1, -1):
            history_item = history[i]
            if isinstance(history_item, ReActItem) and history_item.tool_result:
                self.state.index = i
                break
        await self.__context_process([])

    def __get_tool(self, tool_name: str) -> CommonToolWrapper | None:
        for tool in self.__tools:
            if tool.name == tool_name:
                return tool
        return None

    def __read_history(self) -> List[ReActItem | UserMessageItem]:
        history_json = []
        history = []
        with open(os.path.join(self.state.log_dir, TASK_HISTORY_FILENAME), "r", encoding="utf-8") as f:
            history_json = json.loads(f.read())
        for item in history_json:
            if item.get("message"):
                history.append(UserMessageItem(message=item["message"]))
            if item.get("index"):
                re_act_item = ReActItem(
                    index=item["index"], 
                    reasoning=item["reasoning"], 
                    pure_reasoning=item["pure_reasoning"],
                    tool_call=item["tool_call"],
                    tool_result=ToolCallResult(**item["tool_result"]) if item["tool_result"] else None
                )
                history.append(re_act_item)
        return history

    def __write_history(self, history: List[ReActItem | UserMessageItem]):
        with open(os.path.join(self.state.log_dir, TASK_HISTORY_FILENAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(history, ensure_ascii=False, indent=4, cls=function.DataclassEncoder))

    def __insert_history(self, item: ReActItem | UserMessageItem):
        self.__history.append(item)
        self.__write_history(self.__history)

    def __pop_history(self):
        if self.__history:
            self.__history.pop()
            self.__write_history(self.__history)

    def __set_history(self, history: List[ReActItem | UserMessageItem]):
        self.__history = history
        self.state.history = history
        self.__write_history(self.__history)

    def __set_context(self, enhance_history: List[InputItem], additional_images: List[str] = []):
        self.__context = Context(
            enhance_history=enhance_history,
            additional_images=additional_images
        )

    # TODO: 可深度定制
    async def __context_process(self, additional_images: List[str]):
        # 触发压缩开始事件
        self.__emit(CompressStartEvent())
        
        compressed_result = self.__compressor.compress(state=self.state, memory=self.__memory)
        history_compressed: List[CompressedTaskHistory | ReActItem | UserMessageItem] = []
        if inspect.isasyncgen(compressed_result):
            async for chunk in compressed_result:
                if isinstance(chunk, list) and all(isinstance(item, (CompressedTaskHistory | ReActItem | UserMessageItem)) for item in chunk):
                    history_compressed = chunk
                    break
                self.__emit(CompressYieldEvent(value=chunk))
        elif inspect.iscoroutine(compressed_result):
            history_compressed = await compressed_result
        elif isinstance(compressed_result, list):
            history_compressed = compressed_result

        self.__emit(CompressEndEvent(compressed_history=history_compressed))

        input = []
        for item in history_compressed:
            if isinstance(item, CompressedTaskHistory):
                content = f"\n<compressed_history start_index={item.start_index} end_index={item.end_index}>\n{item.key_info}\n</compressed_history>\n\n"
                input.append(InputItem(role="user", type="text", value=content))
            elif isinstance(item, ReActItem):
                input.append(InputItem(role="assistant", type="text", value=item.reasoning))
                if item.reason_parsed_error:
                    content = item.reason_parsed_error
                    input.append(InputItem(role="user", type="text", value=content))
                if item.tool_result:
                    content = f"<tool_result status={item.tool_result.status}>\n{item.tool_result.content}\n</tool_result>"
                    input.append(InputItem(role="user", type="text", value=content))
            elif isinstance(item, UserMessageItem):
                input.append(InputItem(role="user", type="text", value=item.message))
        self.__set_context(
            enhance_history=input,
            additional_images=additional_images
        )

        # 触发压缩结束事件
        self.__emit(CompressEndEvent(compressed_history=history_compressed))

    def __interrupt(self):
        if self.__reasoning:
            self.__reasoning.cancel()
            self.__reasoning = None
        if self.__tool_calling:
            self.__tool_calling.cancel()
            self.__tool_calling = None

    async def __pending(self):
        while self.status == TaskStatus.STOP:
            await asyncio.sleep(0.1)

    def stop(self):
        self.status = TaskStatus.STOP
        self.__interrupt()

    def continue_task(self):
        self.status = TaskStatus.RUNNING

    def __emit(self, event: Event):
        self.listener.emit(StateSnapshot(self.state), event)

    def end(self):
        self.status = TaskStatus.END
        self.__interrupt()
        # TODO: 做一些处理，比如保存一些信息

    def insert_msg(self, message: str):
        self.stop()
        if self.user_message:
            self.user_message += "\n"
        self.user_message += message
        self.continue_task()

    def re_execute(self, index: int):
        """
        Args:
            index: back to i-th tool call and re-executed.
        """
        self.stop()
        history = self.__history.copy()
        for i in range(len(history) - 1, -1, -1):
            if isinstance(history[i], ReActItem) and history[i].index == index:  # type: ignore
                history = history[:i]
                self.state.index = i
                break
        self.__set_history(history)
        self.continue_task()

    def custom_compressor(self, compressor_func: CustomCompress):
        self.__compressor.set_compress(compressor_func)

    def opt_per_20turns(self):
        if self.state.index % 20 == 0:
            remainders = f"[Repeat emphasizing your system prompt.]\n{self.reasoner_prompt} [Repeat emphasizing user's initial question.]\n{self.state.get_user_question()}"
            self.user_message = remainders + f"\n{self.user_message}" if self.user_message else remainders

    async def run(self) -> TaskResult:
        self.status = TaskStatus.RUNNING
        # 触发任务开始事件
        self.__emit(TaskStartEvent(workspace=self.workspace))
        tool_result: Optional[ToolResult] = None
        additional_images = []
        # FEAT: LOOP
        while not isinstance(tool_result, ToolEnd) and self.state.index <= self.max_turn and self.status != TaskStatus.END:
            await self.__pending()
            self.state.index += 1
            self.opt_per_20turns()
            await self.__context_process(additional_images)
            additional_images = []
            self.__reasoning = asyncio.create_task(self.__reason())
            try:
                content, pure_reasoning, tool_call_object, error = await self.__reasoning
                if error:
                    self.__insert_history(ReActItem(index=self.state.index, reasoning=content, pure_reasoning=pure_reasoning, reason_parsed_error=error))
                    self.__emit(ReasonErrorEvent(error=error))
                    continue
                tool: Optional[CommonToolWrapper] = None
                tool_params: Any = None
                tool_call = None
                tool_name = tool_call_object.get("tool")
                tool_params = tool_call_object.get("params")
                if tool_name and (tool_params is not None):
                    tool = self.__get_tool(tool_name)
                    if tool:
                        tool_call = tool_call_object
                if tool is None or tool_call is None:
                    error = "tool call parse error or no tool choice returned."
                    self.__insert_history(ReActItem(index=self.state.index, reasoning=content, pure_reasoning=pure_reasoning, tool_call=tool_call, reason_parsed_error=error))
                    self.__emit(ReasonErrorEvent(error=error))
                    continue
                self.__emit(ReasonEndEvent(reasoning=content, pure_reasoning=pure_reasoning, tool_call=tool_call))
                self.__insert_history(ReActItem(index=self.state.index, reasoning=content, pure_reasoning=pure_reasoning, tool_call=tool_call))

                self.__tool_calling = asyncio.create_task(self.__tool_call(tool, tool_params))
                tool_result = await self.__tool_calling
                additional_images = tool_result.additional_images if isinstance(tool_result, ToolSuccess) else []

            except asyncio.CancelledError:
                if isinstance(self.__history[-1], ReActItem) and not self.__history[-1].tool_result:
                    self.__pop_history()

        self.status = TaskStatus.END
        if tool_result:
            self.__emit(TaskEndEvent(workspace=self.workspace, status="success"))
            if isinstance(tool_result, ToolEnd):
                return TaskResult(status="end", last_tool=tool_result.name, content=tool_result.content, additional_outputs=tool_result.additional_outputs)
            else:
                return TaskResult(status="interrupt", last_tool=tool_result.name, content=tool_result.content, additional_outputs=None)
        else:
            self.__emit(TaskErrorEvent(workspace=self.workspace, msg="No answer returned due to unknown reasons."))
            return TaskResult(status="error", last_tool="", content="No answer returned due to unknown reasons.")

    async def __reason(self) -> tuple[str, str, dict[str, Any]]:
        try:
            input: List[InputItem] = self.__context.enhance_history
            if self.user_message:
                current_text = self.user_message
            else:
                if self.return_format.lower() == "json":
                    current_text = "Keep thinking and provide tool invocation. The content you return must be within <think> </think> and <tool_call> </tool_call> tag."
                else:
                    current_text = "Keep thinking and provide tool invocation. The content you return must be within <reasoning> </reasoning> and <tool_call> </tool_call> tag."
            before_reason_result = await self.hook.apply_hooks(
                "before_reason",
                self.state,
                current_text
            )
            if before_reason_result is not None:
                current_text = before_reason_result
            input.append(InputItem(role="user", type="text", value=current_text))
            
            with open(os.path.join(self.state.log_dir, TASK_ENHANCE_FILENAME), "w", encoding="utf-8") as f:
                f.write(json.dumps(input, ensure_ascii=False, indent=4, cls=function.DataclassEncoder))

            self.__insert_history(UserMessageItem(message=current_text))
            self.user_message = ""
            if self.__context.additional_images:
                for image in self.__context.additional_images:
                    input.append(InputItem(role="user", type="image", value=image))

            self.__emit(ReasonStartEvent(input=input, system=self.reasoner_prompt))

            content = ""
            async for chunk in self.model.generate(
                system=self.reasoner_prompt,
                input=input,
            ):
                self.__emit(ReasonGenerationEvent(chunk=chunk))
                if isinstance(chunk, ContentChunk | ReasoningChunk):
                    content += chunk.content
            pure_reasoning, json_object, error = function.parse_reason(content, self.return_format)
            return content, pure_reasoning, json_object, error
        except Exception as e:
            raise e
    
    async def __tool_call(self, tool: CommonToolWrapper, tool_params: dict) -> ToolResult:

        def handle_tool_call_result(tool_call_result: ToolResult):
            history = self.__history.copy()
            if isinstance(history[-1], ReActItem) and not history[-1].tool_result:
                history[-1].tool_result = ToolCallResult(tool_call_result.status, tool_call_result.content)
                if isinstance(tool_call_result, ToolSuccess):
                    history[-1].tool_result.additional_images = tool_call_result.additional_images
                elif isinstance(tool_call_result, ToolEnd):
                    history[-1].tool_result.additional_outputs = tool_call_result.additional_outputs
            self.__set_history(history)

            # 根据工具调用结果触发相应事件
            if isinstance(tool_call_result, ToolSuccess):
                self.__emit(ToolSuccessEvent(
                    tool=tool.name,
                    content=tool_call_result.content,
                    additional_images=tool_call_result.additional_images,
                ))
            elif isinstance(tool_call_result, ToolFailed):
                self.__emit(ToolFailedEvent(
                    tool=tool.name,
                    content=tool_call_result.content,
                ))
            elif isinstance(tool_call_result, ToolError):
                self.__emit(ToolErrorEvent(
                    tool=tool.name,
                    content=tool_call_result.content,
                ))
            elif isinstance(tool_call_result, ToolEnd):
                self.__emit(ToolEndEvent(
                    tool=tool.name,
                    content=tool_call_result.content,
                    additional_outputs=tool_call_result.additional_outputs
                ))

        try:
            # 触发工具调用事件
            self.__emit(ToolCallEvent(tool=tool.name, params=tool_params))
            # Tool Call
            invoke_result: Any = tool.invoke(tool_params, self.state)
            tool_call_result: ToolResult = ToolError("No tool call result returned due to unknown reasons.")
            if inspect.isasyncgen(invoke_result):
                async for chunk in invoke_result:
                    if isinstance(chunk, (ToolSuccess | ToolFailed | ToolError | ToolEnd)):
                        tool_call_result = chunk
                        break
                    self.__emit(ToolYieldEvent(tool=tool.name, value=chunk))
            elif inspect.iscoroutine(invoke_result):
                tool_call_result = await invoke_result
            else:
                tool_call_result = invoke_result

            tool_call_result.name = tool.name

            # 应用hook，允许修改工具调用结果
            hook_result = await self.hook.apply_hooks(
                "tool_result",
                self.state,
                ToolHook(tool=tool.name, result=tool_call_result)
            )
            if hook_result is not None:
                hook_result.name = tool.name
                tool_call_result = hook_result

            handle_tool_call_result(tool_call_result)            
            
            return tool_call_result
        except Exception as e:
            tool_call_result = ToolError(content=str(e))
            handle_tool_call_result(tool_call_result)
            return tool_call_result


class InitialTask(TaskBase):

    def __init__(
        self,
        model: Model,
        tools: List[CommonToolWrapper],
        reasoner_prompt: str,
        question: str,
        workspace_root: str,
        workspace_id: str,
        max_turn: int,
        restart_turn: int, # restart and re-execute the task
        custom_compress: Optional[CustomCompress] = None,
        return_format: str = "xml",
    ):
        super().__init__(workspace_root, workspace_id, model, reasoner_prompt, tools, max_turn, restart_turn, return_format)
        self.insert_msg(question)
        if custom_compress:
            self.custom_compressor(custom_compress)


class ExistedTask(TaskBase):
    def __init__(
        self,
        model: Model,
        tools: List[CommonToolWrapper],
        workspace_root: str,
        workspace_id: str,
        reasoner_prompt: str,
        new_max_turn: int,
        restart_turn: int,
        custom_compress: Optional[CustomCompress] = None,
        return_format: str = "xml",
    ):
        super().__init__(workspace_root, workspace_id, model, reasoner_prompt, tools, new_max_turn, restart_turn, return_format)
        if custom_compress:
            self.custom_compressor(custom_compress)
