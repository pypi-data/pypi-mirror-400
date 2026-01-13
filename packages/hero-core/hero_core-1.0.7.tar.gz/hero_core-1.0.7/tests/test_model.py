"""
use pytest -s tests/test_model.py to run the test
"""

from hero import Model
from hero_base import ContentChunk
import pytest

model = Model(
    name="deepseek-chat",
    api_base="https://api.laozhang.ai/v1",
    api_key="sk-123456",
    context_length=128000,
    options={
        "max_tokens": 6000,
        "temperature": 0.7,
    }
)

# @pytest.mark.asyncio
# async def test_model():
#     content = ""
    
#     async for chunk in model.generate(
#         input="what is the result of 1 + 2?",
#         system="You are a helpful assistant. your answer should be in Chinese.",
#     ):
#         if isinstance(chunk, ContentChunk):
#             content += chunk.content
#         print(chunk)

#     print(content)
#     # 添加一个简单的断言来确保测试通过
#     assert len(content) > 0, "应该生成一些内容"


@pytest.mark.asyncio
async def test_json_mode():
    content = ""

    async for chunk in model.generate(
        input="返回根号数学公式符号（使用LaTeX格式）。使用json格式返回。",
        system="",
        response_format={
            "type": "json_object",
        },
    ):
        if isinstance(chunk, ContentChunk):
            content += chunk.content
        print(chunk)

    print(content)
    # 添加一个简单的断言来确保测试通过
    assert len(content) > 0, "应该生成一些内容"