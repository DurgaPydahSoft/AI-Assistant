import logging
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    if not Config.MONGO_URI:
        logging.error("MONGO_URI not found in configuration.")
        return None
    try:
        # Use AsyncIOMotorClient for non-blocking DB calls
        client = AsyncIOMotorClient(Config.MONGO_URI)
        db = client.get_default_database()
        logging.info("Connected to MongoDB via Async Motor")
        return db
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        return None

# Singleton instance
db = get_db()
