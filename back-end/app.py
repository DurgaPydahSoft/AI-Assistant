import logging
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from src.config import Config
from src.database import db
from src.llm import client
from src.schema import get_specific_collection_schema
from src.models import ChatRequest
from pydantic import BaseModel
from src.engine import get_system_prompt, execute_mongo_query, extract_json_actions

app = FastAPI(title="MongoDB AI Assistant API")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For strict security in production, replace with: os.getenv("ALLOWED_ORIGINS", "*").split(",")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []
    ui_context: str = None  # Optional field for UI context

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        messages = [{"role": "system", "content": await get_system_prompt(request.message, request.ui_context)}] + request.history + [{"role": "user", "content": request.message}]
        
        # 1. Try Cache First
        from src.cache import chat_cache
        cached_response = chat_cache.get(messages)
        if cached_response:
            yield f"[Cached Answer]\n{cached_response}"
            return

        full_turn_content = ""
        for _ in range(Config.MAX_STEPS):
            try:
                # 2. Async Client Streaming
                response = await client.chat.completions.create(
                    model=Config.MODEL_NAME,
                    messages=messages,
                    temperature=0.1,
                    stream=True
                )
                
                step_content = ""
                is_json_block = False
                
                async for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    step_content += content
                    
                    # 1. Detect if we are inside a JSON block meant for orchestration
                    if "```json" in step_content and not is_json_block:
                        is_json_block = True
                    
                    # 2. Only yield if it's NOT a hidden orchestration block
                    # Note: There's a tiny chance of leaking "```" if the AI takes several chunks to finish the string,
                    # but for most modern models/chunk sizes, this logic is sufficient.
                    if not is_json_block:
                        # Avoid yielding snippets that are partial starts of ```json
                        if not ("```".startswith(content.strip()) or content.strip().startswith("`")):
                             yield content
                    else:
                        pass # Silently consume orchestration tokens

                full_turn_content += step_content
                actions_data = extract_json_actions(step_content)
                
                if actions_data:
                    # We have at least one action.
                    # We will execute all of them.
                    # Note: For DB queries, executing multiple logic might be complex if they depend on each other.
                    # But for DOM actions, batching is perfect.
                    
                    messages.append({"role": "assistant", "content": step_content})
                    
                    interaction_results = []
                    
                    for action_data in actions_data:
                        action = action_data.get("action")
                        
                        if action == "get_schema":
                            schema_info = await get_specific_collection_schema(db, action_data.get("collections", []))
                            messages.append({"role": "system", "content": f"SCHEMA DATA:\n{schema_info}"})
                            print(f"[LOG] Schema Fetch: {action_data.get('collections')}")
                            
                        elif action in ["query", "insert", "update", "delete"]:
                            print(f"[System]: Executing {action} on {action_data.get('collection')}...")
                            result = await execute_mongo_query(action_data)
                            interaction_results.append(f"Action '{action}': {result}")
                            print(f"[LOG] Action Executed: {action}")
                            
                        elif action == "dom_interaction":
                            print(f"[System]: Converting to Frontend Action: {action_data}")
                            yield f"[DOM_ACTION]{json.dumps(action_data)}[/DOM_ACTION]"
                            interaction_results.append("Action dispatched to UI.")

                    # Should we continue the loop?
                    # If we did any DB actions, we probably want the AI to see the result and formulate an answer.
                    # If we only did DOM actions, we might also want it to say "I've filled the form".
                    
                    if interaction_results:
                        result_summary = "\n".join(interaction_results)
                        messages.append({"role": "user", "content": f"System Execution Results:\n{result_summary}"})
                        continue
                    else:
                        # Actions found but logic skipped? Break to avoid loop.
                        break
                
                # If we reached here without a 'continue', it's the final answer
                chat_cache.set(messages[:-1] + [{"role": "user", "content": request.message}], step_content)
                break
            except Exception as e:
                print(f"ERROR: {e}")
                yield f"\n[Error processing request]\n"
                break

    return StreamingResponse(event_generator(), media_type="text/plain")

class UserModel(BaseModel):
    name: str
    email: str
    bio: str

@app.post("/users")
async def register_user(user: UserModel):
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        doc = user.dict()
        from datetime import datetime
        doc["timestamp"] = datetime.utcnow()
        
        result = await db["users"].insert_one(doc)
        return {"status": "success", "id": str(result.inserted_id)}
    except Exception as e:
        print(f"Registration Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def get_collections():
    from src.schema import get_collection_names
    return {"collections": await get_collection_names(db)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
