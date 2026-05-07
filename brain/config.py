import os
from dotenv import load_dotenv

load_dotenv()

class BrainConfig:
    # LLM API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    MODEL = os.getenv("QWEN_MODEL", "qwen/qwen-2.5-72b-instruct")
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    
    # Memory
    MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", "./memory/memory.db")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./memory/chroma_db")
    
    # Behavior
    MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
    RESPONSE_DELAY_MIN = int(os.getenv("RESPONSE_DELAY_MIN", "30"))
    RESPONSE_DELAY_MAX = int(os.getenv("RESPONSE_DELAY_MAX", "90"))
    
    # Paths
    SOUL_MD_PATH = os.getenv("SOUL_MD_PATH", "./soul/SOUL.md")
    TRUST_LEVELS_PATH = os.getenv("TRUST_LEVELS_PATH", "./soul/trust_levels.json")

config = BrainConfig()
