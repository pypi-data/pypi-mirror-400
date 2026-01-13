from dataclasses import asdict
import json
import os
from datetime import datetime
import re
import xml.etree.ElementTree as ET

from typing import List, Tuple

# TODO: 后期优化，在 Hero 中可以自定义这些参数
SPLIT_FILE_LIMIT = 50000
LINE_LIMIT = 100000
MAX_HISTORY_COUNT = 20
MAX_HISTORY_LIMIT = 40000


class DataclassEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__dataclass_fields__'):
            dict_obj = asdict(o)
            swap = ""
            if "reasoning" in dict_obj:
                swap = dict_obj["reasoning"]
                dict_obj["reasoning"] = dict_obj["pure_reasoning"]
                del dict_obj["pure_reasoning"]
                dict_obj["message"] = swap
            return dict_obj

        return super().default(o)


def parse_param_element(element):
    """
    递归解析 param 及其内部可能的嵌套标签
    """
    # 获取当前节点的类型属性
    p_type = element.get('type', 'string')

    # 检查是否有子节点（如嵌套的 param 或 item）
    children = list(element)

    if not children:
        # 没有子节点，直接返回文本（处理空标签的情况）
        return element.text.strip() if element.text else ""

    if p_type == 'array':
        # 如果是数组，提取所有 item 标签的内容
        # 这里同样递归调用以支持 item 内部嵌套复杂结构
        items = []
        for item in element.findall('item'):
            items.append(parse_param_element(item))
        return items

    # 如果有子节点但不是 array，通常是 object 或嵌套的 param 结构
    res_dict = {}
    for child in children:
        child_name = child.get('name')
        if child_name:
            res_dict[child_name] = parse_param_element(child)
        else:
            # 如果子节点没有 name（比如非标准的嵌套），直接取其文本或递归
            return element.text.strip() if element.text else ""

    return res_dict

def parse_reason_json(content: str) -> tuple[str, List[dict], str]:
    """
    兼容旧版 JSON 返回格式的解析逻辑
    """
    if "</tool_call>" not in content:
        content += "\n</tool_call>"
    reasoning_pattern = re.compile(r'<reasoning>\s*(.+?)\s*</reasoning>', re.DOTALL)
    tool_call_pattern = re.compile(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', re.DOTALL)
    pure_reasoning = ""
    error = ""
    json_objects = []
    reasoning_matches = reasoning_pattern.findall(content)
    tool_call_matches = tool_call_pattern.findall(content)
    for reasoning_str in reasoning_matches:
        pure_reasoning += reasoning_str
    for tool_call_str in tool_call_matches:
        try:
            json_obj = json.loads(tool_call_str)
            if isinstance(json_obj, dict):
                json_objects.append(json_obj)
        except json.JSONDecodeError as e:
            error = f"Failed to decode tool call JSON Object: {tool_call_str}, error: {e}"
    if error:
        return pure_reasoning, json_objects, error
    
    remaining_text = pure_reasoning.strip()
    return remaining_text, json_objects, ""

def parse_reason(xml_string: str, return_format: str = "xml") -> tuple[str, dict, str]:
    """
    根据返回格式解析模型输出，兼容 XML 与 JSON。
    """
    format_key = (return_format or "xml").lower()

    # JSON 兼容：沿用旧的解析逻辑，并取首个工具调用
    if format_key == "json":
        pure_reasoning, json_objects, error = parse_reason_json(xml_string)
        if error:
            return pure_reasoning, {}, error
        tool_call = json_objects[0] if json_objects else {}
        return pure_reasoning, tool_call, ""

    # 默认 XML 解析
    error = ""
    pure_reasoning = ""
    json_object = {}
    try:
        # 如果输入的 XML 片段没有单一根节点，ET 会报错
        # 为了保险，我们将输入包裹在一个自定义根节点中
        wrapped_xml = f"<root>{xml_string}</root>"
        root = ET.fromstring(wrapped_xml)

        # 1. 解析 reasoning
        reasoning_node = root.find('reasoning')
        if reasoning_node is not None:
            pure_reasoning = reasoning_node.text.strip() if reasoning_node.text else ""

        # 2. 解析 tool_call
        tool_node = root.find('tool_call')
        if tool_node is not None:
            tool_name = tool_node.get('name')
            params_dict = {}

            # 找到所有的 param_list 下的一级 param
            param_list_node = tool_node.find('param_list')
            if param_list_node is not None:
                for p in param_list_node.findall('param'):
                    p_name = p.get('name')
                    if p_name:
                        params_dict[p_name] = parse_param_element(p)

            json_object = {
                "tool": tool_name,
                "params": params_dict
            }
    except ET.ParseError as e:
        error = f"XML 解析失败: {str(e)}"
    except Exception as e:
        error = f"处理数据时发生异常: {str(e)}"

    return pure_reasoning, json_object, error


def write_file(dir, file_name, content):
    """
    写入文件
    """
    file_path = os.path.join(dir, file_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def read_file(dir, file_name):
    """
    读取文件
    """
    file_path = os.path.join(dir, file_name)
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def append_file(dir, file_name, content):
    file_path = os.path.join(dir, file_name)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)


def timestamp():
    """
    获取当前时间戳
    """
    return str(int(datetime.now().timestamp()))


def timestamp_to_str(timestamp: str):
    """
    将时间戳转换为字符串
    """
    return datetime.fromtimestamp(int(timestamp)).strftime("%H:%M:%S")


def get_head_and_tail_n_chars(text: str, n: int = 1000) -> str:
    """
    获取文本的头部和尾部指定数量的字符
    """
    if not text:
        return ""
    if len(text) > n:
        half_n = n // 2
        return f"<!-- Original length: {len(text)} bytes, truncated to: head {half_n} bytes and tail {half_n} bytes -->\n{text[:half_n]}\n...\n{text[-half_n:]}"
    return text


def file_to_text_with_line_number(file_path: str) -> str:
    """
    将文件转换为带有行号的文本
    """
    text = ""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        text += "".join([f"{i+1}: {line}" for i, line in enumerate(lines)])
    return text


def clean_tqdm_output(output: str) -> str:
    """Clean tqdm progress bars from output."""
    if not output:
        return ""

    # Remove tqdm progress bars (they typically contain \r and %)
    lines = output.split("\n")
    cleaned_lines = []

    for line in lines:
        # Skip tqdm progress bars
        if "\r" in line and ("%" in line or "it/s" in line):
            continue
        # Skip lines that are just progress indicators
        if line.strip().endswith("%") or line.strip().endswith("it/s"):
            continue
        # Skip lines that are just progress bars
        if re.match(r"^\s*[\d.]+\%|\d+/\d+|\d+it/s", line.strip()):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
