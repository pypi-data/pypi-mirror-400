import sys
import json
import time
from typing import Any, AsyncGenerator, Dict
from hero_base import BasicModel, GenerationChunk, CompletedChunk, Input, ReasoningChunk, ContentChunk, StartChunk, UsageChunk
import httpx
from openai import AsyncOpenAI

class DeepSeekModel(BasicModel):
    def __init__(self, name: str, api_base: str, api_key: str, 
    timeout: int | httpx.Timeout = httpx.Timeout(sys.maxsize, connect=sys.maxsize, read=sys.maxsize, write=sys.maxsize), 
    context_length: int = 128000, options: Dict[str, Any] = {},):
        self.name = name
        self.context_length = context_length
        self.api_base = api_base
        self.api_key = api_key
        self.timeout = timeout
        self.options = options
        
        # 初始化OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base,
            timeout=timeout
        )

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
        try:

            yield StartChunk()

            reasoning_cache = ""
            content_cache = ""
            
            # 存入 message_timestamp 文件
            # with open(f"message_timestamp_{time.time()}", "w", encoding="utf-8") as f:
            #     f.write(json.dumps(messages, ensure_ascii=False, indent=4))

            stream = await self.client.chat.completions.create(
                model=self.name,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},
                **self.options,
                **kwargs
            )
            
            async for chunk in stream:
                if len(chunk.choices) == 0:
                    continue
                if hasattr(chunk.choices[0].delta, "reasoning_content"):
                    reasoning_content = getattr(chunk.choices[0].delta, "reasoning_content") # type: ignore
                    if reasoning_content:
                        reasoning_cache += reasoning_content
                        yield ReasoningChunk(reasoning_content)
                content = chunk.choices[0].delta.content
                if content:
                    content_cache += content
                    yield ContentChunk(content)
                if chunk.usage:
                    yield UsageChunk(chunk.usage.model_dump())
            yield CompletedChunk(content=content_cache, reasoning_content=reasoning_cache)

        except Exception as e:
            raise e