import json
from src.database import db
from src.schema import get_collection_names, get_specific_collection_schema
from src.config import Config
from src.cache import chat_cache

SYSTEM_PROMPT_TEMPLATE = """You are a MongoDB Assistant.
DB: {collections}

TASK:
1. Identify relevant collections.
2. If schema unknown, request: ```json {{ "action": "get_schema", "collections": ["col"] }} ```
3. If ready, generate query:
   ```json
   {{ "action": "query", "collection": "name", "type": "find|count|agg", "filter": {{}}, "pipeline": [], "projection": {{}} }}
   ```
4. Otherwise, reply normally.

RULES:
- Don't guess schema.
- Use regex for searches.
- Result set limit is 10.
"""

def get_system_prompt():
    all_cols = get_collection_names(db)
    return SYSTEM_PROMPT_TEMPLATE.format(collections=all_cols)

def execute_mongo_query(query_data_dict):
    if db is None: return "Error: No database connection."
    try:
        col_name = query_data_dict.get("collection")
        query_type = query_data_dict.get("type", "find")
        collection = db[col_name]
        
        if query_type == "find":
            results = list(collection.find(query_data_dict.get("filter", {}), query_data_dict.get("projection")).limit(10))
        elif query_type == "count":
            return {"count": collection.count_documents(query_data_dict.get("filter", {}))}
        elif query_type == "aggregate":
            results = list(collection.aggregate(query_data_dict.get("pipeline", [])))
        else:
            return f"Error: Unknown query type '{query_type}'"
        
        for doc in results:
            if '_id' in doc: doc['_id'] = str(doc['_id'])
        return results
    except Exception as e:
        return f"Database Error: {str(e)}"

def extract_json_action(content):
    action_data = None
    if "```json" in content:
        try:
            start = content.find("```json") + 7
            end = content.find("```", start)
            action_data = json.loads(content[start:end].strip())
        except: pass
    
    if not action_data and "{" in content and "}" in content:
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            action_data = json.loads(content[start:end].strip())
        except: pass
    return action_data
