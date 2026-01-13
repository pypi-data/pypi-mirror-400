"""
优化的 CLI 监听器工具函数
提供友好的控制台输出格式，支持颜色、图标和结构化显示
使用 colorama 库提供跨平台颜色支持
"""

from colorama import Fore, Back, Style, init as colorama_init
from hero_base import ContentChunk, ReasoningChunk
from hero.event import (
    StateSnapshot, Event, ReasonGenerationEvent, ToolCallEvent,
    ToolSuccessEvent, ToolErrorEvent, ToolEndEvent,
    # ReasonEndEvent, ReasonStartEvent, 
    ReasonErrorEvent,
    TaskStartEvent, TaskEndEvent, TaskErrorEvent,
    ToolFailedEvent, ToolYieldEvent,
    # CompressStartEvent, CompressEndEvent
)

# 初始化 colorama，自动检测终端支持
colorama_init(autoreset=True)


class ListenerConfig:
    """监听器配置类"""

    def __init__(self):
        self.enable_colors = True
        self.enable_icons = True
        self.max_content_length = 200
        self.max_param_length = 50
        self.max_reasoning_length = 300
        self.show_timestamps = False
        self.compact_mode = False

    def disable_colors(self):
        """禁用颜色输出"""
        self.enable_colors = False
        return self

    def disable_icons(self):
        """禁用图标输出"""
        self.enable_icons = False
        return self

    def set_compact_mode(self, enabled=True):
        """设置紧凑模式"""
        self.compact_mode = enabled
        return self


# 全局配置实例
_config = ListenerConfig()

# 全局状态变量用于缓存和工具调用检测
_reasoning_buffer = ""  # 缓存
_in_tool_call = False   # 是否正在处理工具调用


class Colors:
    """使用 colorama 的颜色定义，提供跨平台支持"""
    # 前景色
    HEADER = Fore.MAGENTA      # 紫色
    OKBLUE = Fore.BLUE        # 蓝色
    OKCYAN = Fore.CYAN        # 青色
    OKGREEN = Fore.GREEN      # 绿色
    WARNING = Fore.YELLOW     # 黄色
    FAIL = Fore.RED           # 红色
    WHITE = Fore.WHITE        # 白色
    BLACK = Fore.BLACK        # 黑色

    # 背景色
    BG_HEADER = Back.MAGENTA
    BG_OKBLUE = Back.BLUE
    BG_OKCYAN = Back.CYAN
    BG_OKGREEN = Back.GREEN
    BG_WARNING = Back.YELLOW
    BG_FAIL = Back.RED

    # 样式
    BOLD = Style.BRIGHT       # 粗体/高亮
    DIM = Style.DIM           # 暗淡
    NORMAL = Style.NORMAL     # 正常
    RESET = Style.RESET_ALL   # 重置所有样式

    # 组合样式
    BOLD_HEADER = BOLD + HEADER
    BOLD_OKGREEN = BOLD + OKGREEN
    BOLD_FAIL = BOLD + FAIL
    BOLD_WARNING = BOLD + WARNING


def _apply_color(text, color):
    """根据配置应用颜色"""
    if _config.enable_colors:
        return f"{color}{text}"
    return text


def _apply_icon(text, icon):
    """根据配置应用图标"""
    if _config.enable_icons:
        return f"{icon} {text}"
    return text


def print_separator(char="=", length=60, color=Colors.OKBLUE):
    """打印分隔线"""
    separator = char * length
    if _config.compact_mode:
        length = min(length, 40)
        separator = char * length
    print(_apply_color(separator, color))


def print_header(title, color=Colors.HEADER):
    """打印标题"""
    if _config.compact_mode:
        print(f"\n{_apply_color(f'=== {title} ===', Colors.BOLD_HEADER)}")
    else:
        print(
            f"\n{_apply_color(f'{"=" * 20} {title} {"=" * 20}', Colors.BOLD_HEADER)}")


def print_success(message, icon="✅"):
    """打印成功消息"""
    formatted_message = _apply_icon(message, icon)
    print(f"\n{_apply_color(formatted_message, Colors.BOLD_OKGREEN)}")


def print_error(message, icon="❌"):
    """打印错误消息"""
    formatted_message = _apply_icon(message, icon)
    print(f"\n{_apply_color(formatted_message, Colors.BOLD_FAIL)}")


def print_warning(message, icon="⚠️"):
    """打印警告消息"""
    formatted_message = _apply_icon(message, icon)
    print(f"\n{_apply_color(formatted_message, Colors.BOLD_WARNING)}")


def print_info(message, icon="ℹ️"):
    """打印信息消息"""
    formatted_message = _apply_icon(message, icon)
    print(f"\n{_apply_color(formatted_message, Colors.OKCYAN)}")


def print_tool_call(tool_name, params, index):
    """打印工具调用信息"""
    if not _config.compact_mode:
        print_separator()

    tool_call_text = _apply_icon(f"工具调用 #{index}", "🔧")
    print(_apply_color(tool_call_text, Colors.OKCYAN))

    print(f"{_apply_color('工具名称:', Colors.BOLD)} {_apply_color(tool_name, Colors.OKGREEN)}")
    print(f"{_apply_color('参数:', Colors.BOLD)} {_apply_color(format_tool_params(params), Colors.OKBLUE)}")

    if not _config.compact_mode:
        print_separator("-", 40, Colors.OKCYAN)


def truncate_content(content, max_length=None):
    """截断长内容"""
    if max_length is None:
        max_length = _config.max_content_length
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def format_tool_params(params):
    """格式化工具参数"""
    if not params:
        return "无参数"
    formatted = []
    for key, value in params.items():
        if isinstance(value, str) and len(value) > _config.max_param_length:
            value = value[:_config.max_param_length] + "..."
        formatted.append(f"{key}={value}")
    return ", ".join(formatted)


def _reset_buffers():
    """重置所有缓存"""
    global _reasoning_buffer, _in_tool_call
    _reasoning_buffer = ""
    _in_tool_call = False


def listener_cli_printer(state_snapshot: StateSnapshot, event: Event):
    """
    优化的 CLI 监听器工具函数，提供友好的输出格式

    Args:
        state_snapshot: 状态快照
        event: 事件对象
    """

    # 处理不同类型的事件
    if isinstance(event, ReasonGenerationEvent):
        if isinstance(event.chunk, ContentChunk):
            global _reasoning_buffer, _in_tool_call
            processed_content = event.chunk.content
            # if "```json" in _reasoning_buffer:
            #     processed_content = processed_content.split("```json")[1]
            # _reasoning_buffer += processed_content
            print(processed_content, end="", flush=True)

    elif isinstance(event, ToolCallEvent):
        print_tool_call(event.tool, event.params, state_snapshot.index)

    elif isinstance(event, ToolSuccessEvent):
        print_success(f"工具执行成功: {event.tool}")
        if event.content:
            content = truncate_content(event.content)
            print(f"{Colors.BOLD}结果:{Colors.NORMAL} {Colors.OKBLUE}{content}")
        print_header("")

    elif isinstance(event, ToolErrorEvent):
        print_error(f"工具执行错误: {event.tool}")
        if event.content:
            content = truncate_content(event.content)
            print(f"{Colors.BOLD}错误信息:{Colors.NORMAL} {Colors.FAIL}{content}")

    elif isinstance(event, ToolFailedEvent):
        print_warning(f"工具执行失败: {event.tool}")
        if event.content:
            content = truncate_content(event.content)
            print(f"{Colors.BOLD}失败原因:{Colors.NORMAL} {Colors.WARNING}{content}")

    elif isinstance(event, ToolEndEvent):
        print_success(f"工具执行完成: {event.tool}", "🏁")
        if event.content:
            print(f"{Colors.BOLD}最终结果:{Colors.NORMAL} {Colors.OKBLUE}{event.content}")
        if event.additional_outputs:
            print(f"{Colors.BOLD}额外输出:{Colors.NORMAL} {Colors.OKCYAN}")
            for i, output in enumerate(event.additional_outputs, 1):
                output_preview = str(output)
                print(f"  {i}. {output_preview}")

    elif isinstance(event, ToolYieldEvent):
        # 流式输出
        if isinstance(event.value, ContentChunk):
            print(str(event.value.content), end="", flush=True)
        elif isinstance(event.value, ReasoningChunk):
            print(str(event.value.content), end="", flush=True)

    elif isinstance(event, ReasonErrorEvent):
        print_warning(f"推理错误: {event.error}", "❌")

    elif isinstance(event, TaskStartEvent):
        _reset_buffers()
        print_header("任务开始")
        print(f"{Colors.BOLD}工作空间:{Colors.NORMAL} {Colors.OKGREEN}{event.workspace}")

    elif isinstance(event, TaskEndEvent):
        status_emoji = {"success": "✅", "break": "⏸️",
                        "failed": "❌"}.get(event.status, "❓")
        status_colors = {
            "success": Colors.BOLD_OKGREEN,
            "break": Colors.BOLD_WARNING,
            "failed": Colors.BOLD_FAIL
        }
        status_color = status_colors.get(event.status, Colors.NORMAL)
        print_header(f"任务结束 - {event.status.upper()}")
        print(f"{status_color}{status_emoji} 状态: {event.status}")

    elif isinstance(event, TaskErrorEvent):
        print_header("任务错误")
        print(f"{Colors.BOLD}错误信息:{Colors.NORMAL} {Colors.FAIL}{event.msg}")

    # elif isinstance(event, CompressStartEvent):
    #     print_info("开始压缩历史记录...", "🗜️")

    # elif isinstance(event, CompressEndEvent):
    #     print_success("历史记录压缩完成")
    #     print(
    #         f"{Colors.BOLD}压缩后项目数:{Colors.NORMAL} {Colors.OKBLUE}{len(event.compressed_history)}")

def configure_listener(**kwargs):
    """
    配置监听器选项

    Args:
        enable_colors: 是否启用颜色输出
        enable_icons: 是否启用图标输出
        max_content_length: 最大内容长度
        max_param_length: 最大参数长度
        max_reasoning_length: 最大推理长度
        show_timestamps: 是否显示时间戳
        compact_mode: 是否使用紧凑模式
    """
    global _config

    if 'enable_colors' in kwargs:
        _config.enable_colors = kwargs['enable_colors']
    if 'enable_icons' in kwargs:
        _config.enable_icons = kwargs['enable_icons']
    if 'max_content_length' in kwargs:
        _config.max_content_length = kwargs['max_content_length']
    if 'max_param_length' in kwargs:
        _config.max_param_length = kwargs['max_param_length']
    if 'max_reasoning_length' in kwargs:
        _config.max_reasoning_length = kwargs['max_reasoning_length']
    if 'show_timestamps' in kwargs:
        _config.show_timestamps = kwargs['show_timestamps']
    if 'compact_mode' in kwargs:
        _config.compact_mode = kwargs['compact_mode']


def get_config():
    """获取当前配置"""
    return _config


def reset_config():
    """重置配置为默认值"""
    global _config
    _config = ListenerConfig()
