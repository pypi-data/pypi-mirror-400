import json
from typing import Any, List, Literal, Optional, Dict
import functools
from typing import Callable
from dataclasses import dataclass

from hero_base import ReActItem, Input, State, UserMessageItem
from hero_base.model import GenerationChunk

from hero.compressor.compressor import CompressedTaskHistory

type ListenerName = Literal["all", "task_start", "task_end", "task_error", "reason_start", "reason_generation", "reason_end", "reason_error", "tool_call", "tool_success", "tool_failed", "tool_error", "tool_end", "tool_yield", "compress_start", "compress_yield", "compress_end"]


@dataclass
class Event:
    def __post_init__(self):
        pass
    
    @property
    def name(self) -> str:
        return getattr(self, '_name', '')
    
    @name.setter
    def name(self, value: str):
        self._name = value
    
    def to_dict(self):
        return self.__dict__.copy()
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

@dataclass
class TaskStartEvent(Event):
    workspace: str
    
    def __post_init__(self):
        self.name = "task_start"

@dataclass
class TaskErrorEvent(Event):
    workspace: str
    msg: str

    def __post_init__(self):
        self.name = "task_error"

@dataclass
class TaskEndEvent(Event):
    workspace: str
    status: Literal["success", "break", "failed"]

    def __post_init__(self):
        self.name = "task_end"

@dataclass
class ReasonStartEvent(Event):
    input: Input
    system: str

    def __post_init__(self):
        self.name = "reason_start"

@dataclass
class ReasonGenerationEvent(Event):
    chunk: GenerationChunk

    def __post_init__(self):
        self.name = "reason_generation"

@dataclass
class ReasonEndEvent(Event):
    reasoning: str
    pure_reasoning: str # 去除了工具调用部分的 reasoning
    tool_call: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.name = "reason_end"

@dataclass
class ReasonErrorEvent(Event):
    error: str
    def __post_init__(self):
        self.name = "reason_error"

@dataclass
class ToolCallEvent(Event):
    tool: str
    params: Dict[str, Any]

    def __post_init__(self):
        self.name = "tool_call"

@dataclass
class ToolSuccessEvent(Event):
    tool: str
    content: str
    additional_images: Optional[List[str]] = None

    def __post_init__(self):
        self.name = "tool_success"

@dataclass
class ToolFailedEvent(Event):
    tool: str
    content: str

    def __post_init__(self):
        self.name = "tool_failed"

@dataclass
class ToolErrorEvent(Event):
    tool: str
    content: str

    def __post_init__(self):
        self.name = "tool_error"

@dataclass
class ToolEndEvent(Event):
    tool: str
    content: str
    additional_outputs: Optional[List[str]] = None

    def __post_init__(self):
        self.name = "tool_end"

@dataclass
class ToolYieldEvent(Event):
    tool: str
    value: Any

    def __post_init__(self):
        self.name = "tool_yield"

@dataclass
class CompressStartEvent(Event):

    def __post_init__(self):
        self.name = "compress_start"

@dataclass
class CompressYieldEvent(Event):
    value: Any

    def __post_init__(self):
        self.name = "compress_yield"

@dataclass
class CompressEndEvent(Event):
    compressed_history: List[CompressedTaskHistory | ReActItem | UserMessageItem]

    def __post_init__(self):
        self.name = "compress_end"

class StateSnapshot:
    def __init__(self, state: State):
        self.workspace = state.workspace
        self.working_dir = state.working_dir
        self.log_dir = state.log_dir
        self.index = state.index
        self.history = state.history
        self.__storage = state._storage_snapshot
        self.working_tree = state.get_working_tree()
        self.user_question = state.get_user_question()

    def get_storage(self, key: str, default=None):
        return self.__storage.get(key, default)

class EventListener:
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[StateSnapshot, Event], None]]] = {}
        self._all_listeners: List[Callable[[StateSnapshot, Event], None]] = []
    
    def add_listener(self, event_name: str, listener: Callable[[StateSnapshot, Event], None]):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)
    
    def add_all_listener(self, listener: Callable[[StateSnapshot, Event], None]):
        self._all_listeners.append(listener)
    
    def emit(self, state_snapshot: StateSnapshot, event: Event):
        event_name = getattr(event, 'name', None)
        if event_name and event_name in self._listeners:
            for listener in self._listeners[event_name]:
                listener(state_snapshot, event)

        for listener in self._all_listeners:
            listener(state_snapshot, event)

    def __call__(self, *event_name: ListenerName):
        """
        Event listener decorator
        
        Args:
            event_name: The name of the event, using "all" to listen to all events
        
        Usage:
            @task.listener("all")
            def my_listener(state_snapshot, event):
                print(f"Received event: {event.name}")
            
            @task.listener("task_start")
            def task_start_listener(state_snapshot, event):
                print(f"Task started: {event.workspace}")
        """
        def decorator(func: Callable[[StateSnapshot, Any], None]):
            if "all" in event_name:
                self.add_all_listener(func)
            else:
                for name in event_name:
                    self.add_listener(name, func)
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator