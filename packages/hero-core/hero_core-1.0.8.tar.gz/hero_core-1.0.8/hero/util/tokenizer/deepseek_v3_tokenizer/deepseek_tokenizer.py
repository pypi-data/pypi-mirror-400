import os
import warnings
import logging

# 设置环境变量抑制 transformers 警告
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# 抑制所有 warnings
warnings.filterwarnings("ignore")

# 设置 transformers 日志级别
logging.getLogger("transformers").setLevel(logging.ERROR)

# 获取当前目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(current_dir, use_fast=False, trust_remote_code=True, local_files_only=True)


def token_count(text: str) -> int:
    tokens = tokenizer.encode(text)
    if isinstance(tokens, list):
        return len(tokens)
    elif isinstance(tokens, dict):
        return tokens["length"]
    else:
        return 0