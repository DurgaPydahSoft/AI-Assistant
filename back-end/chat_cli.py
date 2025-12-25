from src.config import Config
from src.database import db
from src.llm import call_llm_stream
from src.schema import get_specific_collection_schema
from src.engine import get_system_prompt, execute_mongo_query, extract_json_action

import asyncio

async def start_chat():
    history = [{"role": "system", "content": await get_system_prompt()}]
    print("\n--- MongoDB AI Assistant (Modular Console) ---")
    print(f"Connected to DB via Async Motor")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            # Note: input() is blocking, but in a CLI this is expected.
            user_input = input("You: ").strip()
            if not user_input: continue
            if user_input.lower() == 'exit': break
            history.append({"role": "user", "content": user_input})
            
            from src.cache import chat_cache
            cached_response = chat_cache.get(history)
            if cached_response:
                print(f"Assistant: [Cached Answer]\n{cached_response}")
                history.append({"role": "assistant", "content": cached_response})
                continue

            for _ in range(Config.MAX_STEPS):
                print("Assistant: ", end="", flush=True)
                step_content = ""
                response = await call_llm_stream(history)
                async for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    print(content, end="", flush=True)
                    step_content += content
                print()

                action_data = extract_json_action(step_content)
                if action_data:
                    action = action_data.get("action")
                    if action == "get_schema":
                        targets = action_data.get("collections", [])
                        print(f"[System]: Fetching schemas for {targets}...")
                        schema_info = await get_specific_collection_schema(db, targets)
                        history.append({"role": "assistant", "content": step_content})
                        history.append({"role": "system", "content": f"SCHEMA DATA:\n{schema_info}"})
                        continue
                    elif action == "query":
                        print(f"[System]: Querying {action_data.get('collection')}...")
                        result = await execute_mongo_query(action_data)
                        history.append({"role": "assistant", "content": step_content})
                        history.append({"role": "user", "content": f"Database Result: {result}\nFormulate final answer."})
                        continue
                
                chat_cache.set(history, step_content)
                history.append({"role": "assistant", "content": step_content})
                break
        except KeyboardInterrupt: break
        except Exception as e: 
            print(f"\n[Fatal Error]: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(start_chat())
