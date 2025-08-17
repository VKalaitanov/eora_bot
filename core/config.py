import os
from dotenv import load_dotenv

load_dotenv()

__version__ = "1.0.0"

# --- Telegram ---
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- OpenAI ---
API_KEY: str = os.getenv("API_KEY", "")
API_BASE_URL: str = os.getenv("API_BASE_URL", "")
MODEL_NAME: str = os.getenv("MODEL_NAME", "mistralai/mistral-7b-instruct")
OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", 0.3))
OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", 600))

# --- Redis ---
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL: int = int(os.getenv("CACHE_TTL", 3 * 60 * 60))  # 3 часа

# --- Parser ---
HEADERS: dict = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
REQUEST_TIMEOUT: int = 10

# --- General ---
BACKGROUND_TASK_INTERVAL: int = 3 * 60 * 60  # 3 часа
