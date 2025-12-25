import json
from src.database import db
from src.schema import get_collection_names, get_specific_collection_schema
from src.config import Config

SYSTEM_PROMPT_TEMPLATE = """You are an advanced MongoDB AI Assistant. Your goal is to help users query their specific MongoDB database.

DATABASE CONTEXT:
- Available Collections: {collections}

INSTRUCTIONS:
1. Every time the user asks a question, first check if any of the "Available Collections" listed above are relevant.
2. If YES, and you need their schema, output a SPECIAL JSON block to request schemas:
   ```json
   {{ "action": "get_schema", "collections": ["coll1", "coll2"] }}
   ```
3. If you have the schema information (provided in a system message) and are ready to query, output a JSON block for the query:
   ```json
   {{
     "action": "query",
     "collection": "Name",
     "type": "find|count|aggregate",
     "filter": {{}},
     "pipeline": [],
     "projection": {{}}
   }}
   ```
4. If it's a general question or you are giving the final answer after seeing results, just reply normally.

CRITICAL:
- Do NOT guess the schema. Use "get_schema" if you haven't seen it yet for a collection.
- Always prefer $regex for user-friendly text searches.
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
