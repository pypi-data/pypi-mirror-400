import os


def read_default_tool_prompt(path: str, params: dict = {}) -> str:
    """
    读取默认提示词
    """
    # 读取相对路径 ./prompt/xxx.md
    current_dir = os.path.dirname(__file__)
    with open(os.path.join(current_dir, "prompt", path), "r", encoding="utf-8") as f:
        prompt = f.read()
        for key, value in params.items():
            if isinstance(value, str):
                prompt = prompt.replace(f"{{{{{key}}}}}", value)
            else:
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        return prompt