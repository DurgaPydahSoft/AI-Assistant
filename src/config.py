import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    API_KEY = os.getenv("API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    MODEL_NAME = "allenai/olmo-3.1-32b-think:free"
    CACHE_TTL = 3600  # 1 hour
    MAX_STEPS = 3

