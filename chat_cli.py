from src.config import Config
from src.database import db
from src.llm import call_llm_stream
from src.schema import get_specific_collection_schema
from src.engine import get_system_prompt, execute_mongo_query, extract_json_action

def start_chat():
    history = [{"role": "system", "content": get_system_prompt()}]
    print("\n--- MongoDB AI Assistant (Modular Console) ---")
    print(f"Connected to: {db.name if db is not None else 'None'}")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input: continue
            if user_input.lower() == 'exit': break
            history.append({"role": "user", "content": user_input})
            
            for _ in range(Config.MAX_STEPS):
                print("Assistant: ", end="", flush=True)
                assistant_content = ""
                response = call_llm_stream(history)
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        assistant_content += content
                print()

                action_data = extract_json_action(assistant_content)
                if action_data:
                    action = action_data.get("action")
                    if action == "get_schema":
                        targets = action_data.get("collections", [])
                        print(f"[System]: Fetching schemas for {targets}...")
                        schema_info = get_specific_collection_schema(db, targets)
                        history.append({"role": "assistant", "content": assistant_content})
                        history.append({"role": "system", "content": f"SCHEMA DATA:\n{schema_info}"})
                        continue
                    elif action == "query":
                        print(f"[System]: Querying {action_data.get('collection')}...")
                        result = execute_mongo_query(action_data)
                        history.append({"role": "assistant", "content": assistant_content})
                        history.append({"role": "user", "content": f"Database Result: {result}\nFormulate final answer."})
                        continue
                history.append({"role": "assistant", "content": assistant_content})
                break
        except KeyboardInterrupt: break
        except Exception as e: print(f"\n[Fatal Error]: {e}")

if __name__ == "__main__":
    start_chat()
