import json
import re
from src.database import db
from src.config import Config
from src.schema import get_collection_names, get_specific_collection_schema
from src.examples import EXAMPLES_BY_CATEGORY

SYSTEM_PROMPT_TEMPLATE = """ROLE: Expert MongoDB Assistant
DB_COLS: {collections}

PERSONALITY & TONE:
- Be proactive, helpful, and highly engaging.
- Use encouraging phrasing like "I'd be happy to help with that!" or "Great question! Let me check that for you."
- Avoid robotic or dry responses. Make the user feel like they are collaborating with an expert.

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
5. [UI Navigation] ->
   - Use the provided `UI_CONTEXT` to find the correct `selector` for navigation.
   - Summarize what you are doing before outputting the JSON block.
6. [Response Flow] -> 
   - Speak ONLY from seen "Database Result". IF DB result is `[]`, state: "I couldn't find any records matching that criteria. Would you like me to try a different search?"
   - **GOAL VERIFICATION**: After every action, check if the user's ultimate goal has been met. If yes, provide a final helpful summary and STOP outputting actions.
   - **CRITICAL**: ALWAYS end your response by providing exactly 3 relevant, interesting follow-up suggestions for the user to click.
   - Format: `[SUGGESTIONS]["Question 1", "Question 2", "Question 3"][/SUGGESTIONS]`
   - Place this tag at the very end of your response.

UI NAVIGATION RULES:
- If user intent involves multiple steps (e.g., "do X then Y"):
  1. You can output multiple `dom_interaction` blocks in a single response to queue them.
  2. Alternatively, output the first action, wait for "System Results", then output the next.
  3. ALWAYS use the exact `selector` from `UI_CONTEXT`.
  4. Sequence: [Thought] -> [Action(s)] -> [SUGGESTIONS]
  5. ❌ NEVER invent a selector. If `UI_CONTEXT` is missing a target, ask for it.

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

    if any(k in msg_low for k in ["go to", "open", "navigate", "click", "tab", "sidebar", "menu"]):
        selected_examples += EXAMPLES_BY_CATEGORY["navigation"]
        
    # Default to search if nothing else matched but we have content
    if not selected_examples and user_message:
        selected_examples = EXAMPLES_BY_CATEGORY["search"]

    # Use provided UI Context or empty
    final_ui_context = f"UI_CONTEXT: {ui_context}" if ui_context else "UI INTERACTION: No specific UI context provided. Do not suggest DOM actions unless user strictly specifies selectors."

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
    
    # 1. Look for markdown blocks with OR without language tag
    # This finds ```json ... ``` AND ``` ... ```
    blocks = re.findall(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
    for block in blocks:
        try:
            data = json.loads(block.strip())
            if isinstance(data, dict):
                actions.append(data)
            elif isinstance(data, list):
                actions.extend([item for item in data if isinstance(item, dict)])
        except:
            pass
            
    # 2. If no actions from blocks, or if we want to be safe, search for raw { } objects
    # This regex attempts to find things that look like objects: { ... }
    # We use a non-greedy .*? but need to balance braces for deeper nesting if possible
    # For now, a simple regex or a balanced search is better.
    if not actions:
        # Simple regex for finding content between { and }
        # This can be greedy, so we find the inner-most or specific structures
        raw_matches = re.findall(r"({[^{]*?\"action\"[^{]*?})", content, re.DOTALL)
        for raw in raw_matches:
            try:
                data = json.loads(raw.strip())
                if isinstance(data, dict) and "action" in data:
                    actions.append(data)
            except:
                pass

    # 3. Last resort: finding by explicit markers if they were leaked
    if not actions and "[DOM_ACTION]" in content:
        # This is for cases where the model might already be trying to output our internal format
        marks = re.findall(r"\[DOM_ACTION\](.*?)\[/DOM_ACTION\]", content, re.DOTALL)
        for m in marks:
            try:
                data = json.loads(m.strip())
                actions.append(data)
            except: pass

    return actions
