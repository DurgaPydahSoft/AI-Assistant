import json
from src.database import db
from src.config import Config
from src.schema import get_collection_names, get_specific_collection_schema
from src.examples import EXAMPLES_BY_CATEGORY

SYSTEM_PROMPT_TEMPLATE = """ROLE: Expert MongoDB Assistant
DB_COLS: {collections}

PROTOCOL:
1. [Schema Missing] -> Output: ```json {{ "action": "get_schema", "collections": ["..."] }} ```
2. [Data Needed] -> Output: ```json {{ "action": "query|insert|update|delete", "collection": "...", "type": "find|count|agg", "filter": {{}}, "pipeline": [], "document": {{}}, "update": {{}} }} ```
3. [Data Available] -> Speak ONLY from seen "Database Result".

STRICT TRUTH POLICY:
- ❌ NEVER invent data or use placeholders (e.g., example.com).
- ✅ IF DB result is `[]`, state: "No records found."

EXAMPLES:
{examples}

SEARCH INTELLIGENCE:
- Map user intent to fields. Use `$or` for multi-field ambiguity.
- Always use `$regex` with `$options: "i"` for strings.

RULES:
- Limit: Max {limit} docs per query.
- Precision: ALWAYS use specific filters for Update/Delete to avoid bulk accidental changes.
"""

async def get_system_prompt(user_message=""):
    all_cols = await get_collection_names(db)
    
    # Dynamic Example Selection
    selected_examples = ""
    msg_low = user_message.lower()
    
    if any(k in msg_low for k in ["how many", "count", "average", "avg", "sum", "total", "math"]):
        selected_examples += EXAMPLES_BY_CATEGORY["aggregation"]
    
    if any(k in msg_low for k in ["add", "insert", "create", "update", "change", "set", "remove", "delete", "delete", "edit"]):
        selected_examples += EXAMPLES_BY_CATEGORY["crud"]
    
    # If it looks like a person/contact search or ambiguous query
    if any(k in msg_low for k in ["find", "search", "who is", "email", "phone", "contact", "name"]):
        selected_examples += EXAMPLES_BY_CATEGORY["search"]
        
    # Default to search if nothing else matched but we have content
    if not selected_examples and user_message:
        selected_examples = EXAMPLES_BY_CATEGORY["search"]

    return SYSTEM_PROMPT_TEMPLATE.format(
        collections=all_cols, 
        examples=selected_examples,
        limit=Config.DEFAULT_LIMIT
    )

async def execute_mongo_query(query_data_dict):
    if db is None: return "Error: No database connection."
    try:
        action = query_data_dict.get("action", "query")
        col_name = query_data_dict.get("collection")
        collection = db[col_name]
        limit = Config.DEFAULT_LIMIT
        
        if action == "query":
            query_type = query_data_dict.get("type", "find")
            if query_type == "find":
                cursor = collection.find(query_data_dict.get("filter", {}), query_data_dict.get("projection")).limit(limit)
                results = await cursor.to_list(length=limit)
            elif query_type == "count":
                count = await collection.count_documents(query_data_dict.get("filter", {}))
                return {"count": count}
            elif query_type == "aggregate":
                cursor = collection.aggregate(query_data_dict.get("pipeline", []))
                results = await cursor.to_list(length=limit)
            else:
                return f"Error: Unknown query type '{query_type}'"
            
            for doc in results:
                if '_id' in doc: doc['_id'] = str(doc['_id'])
            return results

        elif action == "insert":
            doc = query_data_dict.get("document", {})
            result = await collection.insert_one(doc)
            return {"status": "success", "inserted_id": str(result.inserted_id)}

        elif action == "update":
            filter_data = query_data_dict.get("filter", {})
            update_data = query_data_dict.get("update", {})
            if not filter_data: return "Error: Update requires a filter for safety."
            result = await collection.update_many(filter_data, update_data)
            return {"status": "success", "matched_count": result.matched_count, "modified_count": result.modified_count}

        elif action == "delete":
            filter_data = query_data_dict.get("filter", {})
            if not filter_data: return "Error: Delete requires a filter for safety."
            result = await collection.delete_many(filter_data)
            return {"status": "success", "deleted_count": result.deleted_count}

        else:
            return f"Error: Unknown action '{action}'"

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
