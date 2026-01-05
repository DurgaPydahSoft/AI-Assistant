import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    API_KEY = os.getenv("API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    MODEL_NAME = "qwen/qwen-2.5-vl-7b-instruct:free"
    #MODEL_NAME = "xiaomi/mimo-v2-flash:free"
    #MODEL_NAME = "mistralai/mistral-7b-instruct:free"
    CACHE_TTL = 3600  # 1 hour
    MAX_STEPS = 10
    DEFAULT_LIMIT = 50

