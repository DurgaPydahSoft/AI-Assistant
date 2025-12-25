from openai import OpenAI
from src.config import Config
import time
import random

client = OpenAI(
    api_key=Config.API_KEY,
    base_url=Config.OPENROUTER_BASE_URL,
)

def call_llm_stream(messages, temperature=0.1):
    try:
        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=messages,
            temperature=temperature,
            stream=True
        )
        return response
    except Exception as e:
        raise e

def call_llm_with_retry(messages, temperature=0.1, max_retries=3):
    base_delay = 2
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "500" in error_msg:
                wait_time = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                if attempt == max_retries - 1: raise e
                time.sleep(1)
    return None
