import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

# 记忆存储路径
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "data", "memory.json")

# 提取设置
EXTRACT_BATCH_SIZE = 10  # 每 N 轮对话触发一次提取
MAX_CONTEXT_ENTRIES = 20  # 注入 system prompt 的最大条目数
