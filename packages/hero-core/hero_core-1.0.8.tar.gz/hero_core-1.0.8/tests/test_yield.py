import asyncio
from typing import AsyncGenerator, Union


# 方法1: 使用特殊的标记值（最推荐）
class Sentinel:
    """特殊的结束标记"""
    def __init__(self, value=None):
        self.value = value

async def test_yield_with_sentinel():
    yield "hello"
    yield "world"
    yield Sentinel("这是最终结果")  # 使用特殊对象作为结束标记

async def test_yield_with_sentinel_process():
    async for chunk in test_yield_with_sentinel():
        if isinstance(chunk, Sentinel):
            print(f"最终结果: {chunk.value}")
            break
        print(f"yield的值: {chunk}")


# 方法2: 使用None作为结束标记
async def test_yield_with_none():
    yield "hello"
    yield "world"
    yield None  # 使用None作为结束标记

async def test_yield_with_none_process():
    async for chunk in test_yield_with_none():
        if chunk is None:
            print("检测到结束标记")
            break
        print(f"yield的值: {chunk}")


# 方法3: 使用包装类
class YieldResult:
    def __init__(self, value, is_final=False):
        self.value = value
        self.is_final = is_final

async def test_yield_with_wrapper():
    yield YieldResult("hello")
    yield YieldResult("world")
    yield YieldResult("这是最终结果", is_final=True)

async def test_yield_with_wrapper_process():
    async for result in test_yield_with_wrapper():
        if result.is_final:
            print(f"最终结果: {result.value}")
        else:
            print(f"yield的值: {result.value}")


# 方法4: 使用异常来传递返回值
class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__()

async def test_yield_with_exception():
    yield "hello"
    yield "world"
    raise ReturnValue("这是通过异常传递的返回值")

async def test_yield_with_exception_process():
    try:
        async for chunk in test_yield_with_exception():
            print(f"yield的值: {chunk}")
    except ReturnValue as e:
        print(f"返回值: {e.value}")


# 方法5: 使用asend()手动控制（可以获取StopAsyncIteration的value）
async def test_manual_control():
    async def manual_generator():
        yield "hello"
        yield "world"
        raise StopAsyncIteration("这是手动控制的返回值")
    
    gen = manual_generator()
    try:
        while True:
            value = await gen.asend(None)
            print(f"手动获取的值: {value}")
    except RuntimeError as e:
        if "StopAsyncIteration" in str(e):
            # 在Python 3.7+中，我们需要通过其他方式获取返回值
            # 这里我们无法直接获取StopAsyncIteration的value
            print("检测到生成器结束，但无法直接获取返回值")
        else:
            raise


# 方法6: 使用元组来区分类型
async def test_yield_with_tuple():
    yield ("data", "hello")
    yield ("data", "world")
    yield ("result", "这是最终结果")

async def test_yield_with_tuple_process():
    async for item_type, value in test_yield_with_tuple():
        if item_type == "result":
            print(f"最终结果: {value}")
        else:
            print(f"yield的值: {value}")


async def main():
    print("=== 方法1: 使用特殊标记对象 ===")
    await test_yield_with_sentinel_process()
    
    print("\n=== 方法2: 使用None作为结束标记 ===")
    await test_yield_with_none_process()
    
    print("\n=== 方法3: 使用包装类 ===")
    await test_yield_with_wrapper_process()
    
    print("\n=== 方法4: 使用异常传递返回值 ===")
    await test_yield_with_exception_process()
    
    print("\n=== 方法5: 手动控制（可以获取StopAsyncIteration的value） ===")
    await test_manual_control()
    
    print("\n=== 方法6: 使用元组区分类型 ===")
    await test_yield_with_tuple_process()

if __name__ == "__main__":
    asyncio.run(main())