import os
from dotenv import load_dotenv

load_dotenv()

# 模型配置
MODELS = {
    "deepseek": {
        "name": "DeepSeek V4 Flash",
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        "api_type": "openai",
    },
    "mimo": {
        "name": "MiMo v2.5 Pro",
        "base_url": os.getenv("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/anthropic"),
        "api_key": os.getenv("MIMO_API_KEY", ""),
        "model": os.getenv("MIMO_MODEL", "mimo-v2.5-pro"),
        "api_type": "anthropic",
    },
}

# 当前使用的模型
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek")

# 记忆存储路径
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "data", "memory.json")

# 提取设置
EXTRACT_BATCH_SIZE = 10
MAX_CONTEXT_ENTRIES = 20
