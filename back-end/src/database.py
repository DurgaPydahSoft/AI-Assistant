import logging
from pymongo import MongoClient
from src.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    if not Config.MONGO_URI:
        logging.error("MONGO_URI not found in configuration.")
        return None
    try:
        client = MongoClient(Config.MONGO_URI)
        db = client.get_database()
        logging.info(f"Connected to MongoDB: {db.name}")
        return db
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        return None

# Singleton instance
db = get_db()
