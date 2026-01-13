from typing import Any, AsyncGenerator, Callable, Coroutine, List, Optional
import re

from dataclasses import dataclass
from hero_base import ContentChunk, Memory, State, ReActItem, UserMessageItem
from hero.build_in_model import Model
from hero.util.tokenizer.deepseek_v3_tokenizer.deepseek_tokenizer import token_count

compress_prompt = """
You are a super-intelligent AI assistant with exceptional summarization capabilities. Your objective is to provide a detailed yet succinct summary of the key points from the user's provided history.

<basic_rules>
Adhere to these rules:

- Deliver a concise, detailed summary by highlighting critical information, focusing on both positive and negative outcomes in a balanced manner.
- In the case of multiple experimental results, give priority to elements that influence the results positively, but include brief notes on negatively impacting factors.
- Choose an efficient format to present the summary, ensuring clarity and conciseness.
- Do not invent details; stay true to the user's content.
- Ensure no crucial user information is left out.
- Enclose the final, polished summary within the compress_summary XML tag.
</basic_rules>

<return_example>
Your detailed insights on the user's content
<compress_summary>
the enhanced summary content
</compress_summary>
</return_example>
"""

secondary_compress_prompt = """
You are a super-intelligent AI assistant with exceptional summarization capabilities. Your objective is to provide a detailed yet succinct summary of the key points from the user's provided history.
The user's history brief will be wrapped using XML tags, where the index attribute indicates that this summary occurred during the conversation between start_index and end_index rounds in the large model dialogue.
Your task is to distill the essential elements from the target history.

<basic_rules>
Adhere to these rules:

- Deliver a concise, detailed summary by highlighting critical information, focusing on both positive and negative outcomes in a balanced manner.
- In the case of multiple experimental results, give priority to elements that influence the results positively, but include brief notes on negatively impacting factors.
- Choose an efficient format to present the summary, ensuring clarity and conciseness.
- Do not invent details; stay true to the user's content.
- Ensure no crucial user information is left out.
- Enclose the final, polished summary within the compress_summary XML tag.
</basic_rules>

<return_example>
Your detailed insights on the user's content
<compress_summary>
the enhanced summary content
</compress_summary>
</return_example>
"""


@dataclass
class CompressedTaskHistory:
    start_index: int
    end_index: int
    key_info: str

type CustomCompress = Callable[[State, Memory], List[CompressedTaskHistory | ReActItem | UserMessageItem] | Coroutine[Any, Any, List[CompressedTaskHistory | ReActItem | UserMessageItem]] | AsyncGenerator[Any, List[CompressedTaskHistory | ReActItem | UserMessageItem]]] 

# TODO: 验证不同类型压缩器是否工作正常
class Compressor:

    def __init__(self, compressor_model: Model):
        self.compressor_model = compressor_model
        self.custom_compress: Optional[CustomCompress] = None
    
    def _extract_compress_summary(self, text: str) -> str:
        """
        从文本中提取 <compress_summary> 标签内的内容
        
        Args:
            text: 包含标签的文本
            
        Returns:
            提取的标签内容，如果未找到标签则返回空字符串
        """
        try:
            # 使用正则表达式匹配 <compress_summary> 标签内容
            pattern = r'<compress_summary>(.*?)</compress_summary>'
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            
            if match:
                content = match.group(1).strip()
                return content
            else:
                # 如果没有找到标签，尝试查找可能的变体
                # 处理可能的格式问题，如缺少结束标签
                start_pattern = r'<compress_summary>(.*?)(?=<|$)'
                start_match = re.search(start_pattern, text, re.DOTALL | re.IGNORECASE)
                
                if start_match:
                    content = start_match.group(1).strip()
                    return content
                
                # 如果仍然没有找到，返回整个文本作为备选
                return text.strip()
                
        except Exception as e:
            # 如果解析过程中出现错误，记录并返回空字符串
            print(f"Warning: Failed to extract compress_summary: {e}")
            return ""
    
    async def _compress(self, state: State, memory: Memory) -> List[CompressedTaskHistory | ReActItem | UserMessageItem]:
        
        history = state.history.copy() # type: ignore 

        if len(history) == 0:
            return []

        compress_index = memory.get("compress_index", 0)
        history_message = ""

        # 获取未压缩的历史
        for item in history[compress_index:]:
            if isinstance(item, UserMessageItem):
                history_message += f"<user_message>\n{item.message}\n</user_message>\n"
            elif isinstance(item, ReActItem):
                history_message += f"<react_item>\n{item.reasoning}\n</react_item>\n"
                if item.tool_result:
                    history_message += f"<tool_result>\n{item.tool_result.content}\n</tool_result>\n"
                if item.reason_parsed_error:
                    history_message += f"<reason_parsed_error>\n{item.reason_parsed_error}\n</reason_parsed_error>\n"

        if token_count(history_message) > 24000:
            if len(memory.records) > 0:
                input = f"<user_message>\n{history[0].message}\n</user_message>\n"
            else:
                input = ""
            input += "<historical_brief>\n"
            for item in memory.records:
                input += f"{item.key_info}\n"
            input += f"</historical_brief>\n"
            input += f"<target_history>\n{history_message}\n</target_history>\n"
            
            cache = ""
            async for chunk in self.compressor_model.generate(
                input=input,
                system=compress_prompt,
            ):
                if isinstance(chunk, ContentChunk):
                    cache += chunk.content
            
            # 解析 cache，提取 <compress_summary> 标签内的内容
            key_info = self._extract_compress_summary(cache)

            # 保存压缩后的历史
            compressed_task_history = CompressedTaskHistory(
                start_index=compress_index,
                end_index=len(history),
                key_info=key_info,
            )
            memory.records.append(compressed_task_history)
            memory.set("compress_index", len(history))

            # 二次压缩
            compressed_histories = f"<user_message>\n{history[0].message}\n</user_message>\n"
            for item in memory.records:
                compressed_histories += f"<history_brief start_index={item.start_index} end_index={item.end_index}>\n{item.key_info}\n</history_brief>\n"
            if token_count(compressed_histories) > 24000:
                cache = ""
                async for chunk in self.compressor_model.generate(
                    input= compressed_histories,
                    system=secondary_compress_prompt,
                ):
                    if isinstance(chunk, ContentChunk):
                        cache += chunk.content
                key_info = self._extract_compress_summary(cache)
                compressed_task_history = CompressedTaskHistory(
                    start_index=0,
                    end_index=len(history),
                    key_info=key_info,
                )
                memory.records = [compressed_task_history]

            return [history[0], *memory.records]

        if len(memory.records) == 0:
            return [*history]
        else:
            return [history[0], *memory.records, *history[compress_index:]]

    def compress(self, state: State, memory: Memory):
        if self.custom_compress:
            return self.custom_compress(state, memory)

        return self._compress(state, memory)

    def set_compress(self, compress_func: CustomCompress):
        self.custom_compress = compress_func