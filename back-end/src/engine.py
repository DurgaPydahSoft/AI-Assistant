import json
import re
from src.database import db
from src.config import Config
from src.schema import get_collection_names, get_specific_collection_schema
from src.examples import EXAMPLES_BY_CATEGORY

SYSTEM_PROMPT_TEMPLATE = """ROLE: Expert MongoDB Assistant
DB_COLS: {collections}

PROTOCOL:
1. [Missing Info/Schema] -> 
   - Before suggesting an `insert` or `update`, you MUST call `get_schema` if you haven't seen the schema yet.
   - If fields required by the schema are missing from user input, ASK the user to provide them.
   - Output: ```json {{ "action": "get_schema", "collections": ["..."] }} ```
2. [Pending Execution] -> 
   - For `insert`, `update`, or `delete`, you MUST first summarize the action to the user and ask for CLEAR CONFIRMATION (e.g., "Shall I proceed?").
   - DO NOT output the execution JSON block until the user says "Yes", "Proceed", "Confirm", or similar.
3. [Executing Data Action] -> 
   - ONLY after user confirmation, output: ```json {{ "action": "query|insert|update|delete", "collection": "...", "type": "find|count|agg", "filter": {{}}, "pipeline": [], "document": {{}}, "update": {{}} }} ```
4. [DOM Interaction] -> Output: ```json {{ "action": "dom_interaction", "target": "#selector", "type": "click|type", "value": "..." }} ```
5. [Response Flow] -> Speak ONLY from seen "Database Result". IF DB result is `[]`, state: "No records found."

STRICT TRUTH POLICY:
- ❌ NEVER invent data or use placeholders.
- ✅ ONLY execute write actions AFTER explicit user approval.

EXAMPLES:
{examples}

RULES:
- Limit: Max {limit} docs per query.
- Update/Delete: ALWAYS use specific filters. If searching by name, verify the record exists first.
"""

async def get_system_prompt(user_message="", ui_context=""):
    all_cols = await get_collection_names(db)
    
    # Dynamic Example Selection
    selected_examples = ""
    msg_low = user_message.lower()
    
    # Always include iterative for safety if any write/edit intent is detected
    if any(k in msg_low for k in ["add", "insert", "create", "update", "change", "set", "remove", "delete", "edit", "modify"]):
        selected_examples += EXAMPLES_BY_CATEGORY["iterative"]
    
    if any(k in msg_low for k in ["how many", "count", "average", "avg", "sum", "total", "math"]):
        selected_examples += EXAMPLES_BY_CATEGORY["aggregation"]
    
    # If it looks like a person/contact search or ambiguous query
    if any(k in msg_low for k in ["find", "search", "who is", "email", "phone", "contact", "name"]):
        selected_examples += EXAMPLES_BY_CATEGORY["search"]
        
    # Default to search if nothing else matched but we have content
    if not selected_examples and user_message:
        selected_examples = EXAMPLES_BY_CATEGORY["search"]

    # Use provided UI Context or empty
    final_ui_context = ui_context if ui_context else "UI INTERACTION: No specific UI context provided. Do not suggest DOM actions unless user strictly specifies selectors."

    return SYSTEM_PROMPT_TEMPLATE.format(
        collections=all_cols, 
        examples=selected_examples + "\n" + final_ui_context,
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

def extract_json_actions(content):
    actions = []
    # 1. Try to find all markdown json blocks
    # Use regex to find contents between ```json and ```
    matches = re.findall(r"```json(.*?)```", content, re.DOTALL)
    
    for match in matches:
        try:
            data = json.loads(match.strip())
            actions.append(data)
        except:
            pass
            
    # 2. If no markdown blocks, try to parse the whole string or find outer braces
    if not actions and "{" in content and "}" in content:
        try:
             # Fallback: try to find the first valid JSON object
             # This is a bit brittle for multiple objects without delimiters
             # So we prioritize the markdown blocks.
             start = content.find("{")
             end = content.rfind("}") + 1
             data = json.loads(content[start:end].strip())
             actions.append(data)
        except: pass
        
    return actions
