from dataclasses import dataclass
import sys
import asyncio
from typing import Any, AsyncGenerator, Dict
from hero_base import BasicModel, GenerationChunk, CompletedChunk, Input, ContentChunk, StartChunk
from openai import AsyncOpenAI

@dataclass
class LLMInfo:
    client: AsyncOpenAI
    queue_size: int

class RLModel(BasicModel):
    def __init__(self, name: str, api_base: str | list[str], api_key: str, timeout: int = sys.maxsize, context_length: int = 128000, options: Dict[str, Any] = {},):
        self.name = name
        self.context_length = context_length
        if isinstance(api_base, list):
            self.api_list = api_base
        else:
            self.api_list = [api_base]
        self.api_key = api_key
        self.timeout = timeout
        self.options = options
        
        self.llm_dict: Dict[str, LLMInfo] = {}

        for api_base in self.api_list:
            self.llm_dict[api_base] = LLMInfo(
                client=AsyncOpenAI(
                    api_key=api_key,
                    base_url=api_base,
                    timeout=timeout
                ),
                queue_size=0
            )

    def get_llm(self) -> LLMInfo:
        sorted_llm_dict = sorted(self.llm_dict.values(), key=lambda x: x.queue_size)
        llm_info = sorted_llm_dict[0]
        llm_info.queue_size += 1
        return llm_info
    
    def release_llm(self, llm_info: LLMInfo):
        llm_info.queue_size -= 1

    async def generate(self, input: Input, system: str = "", *args, **kwargs) -> AsyncGenerator[GenerationChunk, None]:
        messages = [{"role": "system", "content": system}]

        if isinstance(input, str):
            messages.append({"role": "user", "content": input})
        else:
            index = 0
            while index < len(input):
                item = input[index]
                if item.role == "user":
                    content = ""
                    while item.role == "user":
                        if item.type == "text":
                            content += f"{item.value}\n"
                        index += 1
                        if index >= len(input):
                            break
                        item = input[index]
                    messages.append({"role": "user", "content": content.strip()})
                if item.role == "assistant":
                    messages.append({"role": "assistant", "content": item.value})
                if item.role == "system":
                    messages.append({"role": "system", "content": item.value})
                index += 1
        yield StartChunk()

        llm = self.get_llm()

        # 重试机制
        max_retries = 3
        retry_delay = 1.0  # 1秒延迟
        
        for attempt in range(max_retries):
            try:
                response = await llm.client.chat.completions.create(
                    model=self.name,
                    messages=messages,
                    max_tokens=8000,
                    # stream=True,
                    # stream_options={"include_usage": True},
                    **self.options,
                    **kwargs
                )

                content = response.choices[0].message.content
                yield ContentChunk(content)
                yield CompletedChunk(content=content, reasoning_content="")
                self.release_llm(llm)
                return  # 成功则直接返回
                
            except Exception as e:
                if attempt < max_retries - 1:  # 不是最后一次尝试
                    await asyncio.sleep(retry_delay)
                else:  # 最后一次尝试失败
                    self.release_llm(llm)
                    raise e