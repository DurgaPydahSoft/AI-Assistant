import hashlib
import json
import time
from src.config import Config

class ResponseCache:
    """
    A simple in-memory cache for storing AI responses based on message history.
    In a production app, this could be backed by Redis or MongoDB.
    """
    def __init__(self, ttl=Config.CACHE_TTL):
        self.cache = {}
        self.ttl = ttl

    def _generate_key(self, messages):
        # Create a stable hash based on the dialogue history
        # We only hash the role and content to stay consistent
        serializable = [{"r": m["role"], "c": m["content"]} for m in messages]
        msg_str = json.dumps(serializable, sort_keys=True)
        return hashlib.sha256(msg_str.encode()).hexdigest()

    def get(self, messages):
        key = self._generate_key(messages)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["response"]
            else:
                del self.cache[key]
        return None

    def set(self, messages, response):
        key = self._generate_key(messages)
        self.cache[key] = {
            "response": response,
            "timestamp": time.time()
        }

# Global singleton
chat_cache = ResponseCache()
