import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from src.config import Config
from src.database import db
from src.llm import client
from src.schema import get_specific_collection_schema
from src.models import ChatRequest
from src.engine import get_system_prompt, execute_mongo_query, extract_json_action

app = FastAPI(title="MongoDB AI Assistant API")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        messages = [{"role": "system", "content": get_system_prompt()}] + request.history + [{"role": "user", "content": request.message}]
        
        for _ in range(Config.MAX_STEPS):
            try:
                response = client.chat.completions.create(
                    model=Config.MODEL_NAME,
                    messages=messages,
                    temperature=0.1,
                    stream=True
                )
                
                full_content = ""
                for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    full_content += content
                    yield content

                action_data = extract_json_action(full_content)
                if action_data:
                    action = action_data.get("action")
                    if action == "get_schema":
                        schema_info = get_specific_collection_schema(db, action_data.get("collections", []))
                        messages.append({"role": "assistant", "content": full_content})
                        messages.append({"role": "system", "content": f"SCHEMA DATA:\n{schema_info}"})
                        yield "\n[System: Schema Fetched]\n"
                        continue
                    elif action == "query":
                        result = execute_mongo_query(action_data)
                        messages.append({"role": "assistant", "content": full_content})
                        messages.append({"role": "user", "content": f"Database Result: {result}\nFormulate final answer."})
                        yield f"\n[System: Executed query on {action_data.get('collection')}]\n"
                        continue
                break
            except Exception as e:
                yield f"\n[Error: {e}]\n"
                break

    return StreamingResponse(event_generator(), media_type="text/plain")

@app.get("/collections")
async def get_collections():
    from src.schema import get_collection_names
    return {"collections": get_collection_names(db)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
