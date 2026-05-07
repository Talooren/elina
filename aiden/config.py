import os
from dotenv import load_dotenv

load_dotenv()

class AidenConfig:
    # LLM
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    MODEL = os.getenv("QWEN_MODEL", "qwen/qwen-2.5-72b-instruct")
    
    # Telegram канал
    TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID", "@elina_moments")
    
    # Twitter
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
    
    # Instagram
    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
    
    # Rate limits (жёсткие!)
    MAX_POSTS_PER_DAY_TG = 4
    MAX_POSTS_PER_DAY_TWITTER = 6
    MAX_POSTS_PER_DAY_IG = 3
    
    # Агент
    MAX_STEPS_PER_TASK = 10
    BUDGET_PER_SESSION = 0.50  # USD
    TASK_TIMEOUT = 300  # seconds
    
    # Paths
    SOUL_MD_PATH = "./soul/SOUL.md"
    SKILLS_DIR = "./aiden/skills"
