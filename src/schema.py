import time
from datetime import datetime
from bson import ObjectId
from src.config import Config

# --- Schema Cache ---
SCHEMA_CACHE = {}

def map_field_type(value):
    if isinstance(value, str): return "String"
    if isinstance(value, int): return "Integer"
    if isinstance(value, float): return "Float"
    if isinstance(value, bool): return "Boolean"
    if isinstance(value, list): return "List"
    if isinstance(value, dict): return "Object"
    if isinstance(value, ObjectId): return "ObjectId"
    if isinstance(value, datetime): return "DateTime"
    return str(type(value).__name__) if value is not None else "Null"

def analyze_collection_schema(collection, sample_size=10, force_refresh=False):
    col_name = collection.name
    now = time.time()
    
    if not force_refresh and col_name in SCHEMA_CACHE:
        cache_entry = SCHEMA_CACHE[col_name]
        if now - cache_entry["timestamp"] < Config.CACHE_TTL:
            return cache_entry["schema"]
    
    schema = {}
    try:
        pipeline = [{"$sample": {"size": sample_size}}]
        docs = list(collection.aggregate(pipeline))
    except:
        docs = list(collection.find().limit(sample_size))
    
    if not docs: return {}
    
    for doc in docs:
        for key, value in doc.items():
            if key not in schema: schema[key] = set()
            schema[key].add(map_field_type(value))
    
    final_schema = {k: ", ".join(sorted(list(v))) for k, v in schema.items()}
    SCHEMA_CACHE[col_name] = {"schema": final_schema, "timestamp": now}
    return final_schema

def get_collection_names(db):
    return db.list_collection_names() if db is not None else []

def get_specific_collection_schema(db, target_collections):
    if db is None: return "No database connection."
    summary_lines = []
    available = db.list_collection_names()
    for col_name in target_collections:
        if col_name not in available: continue
        schema = analyze_collection_schema(db[col_name], sample_size=3)
        fields = [f"{k}:{v}" for k, v in schema.items()]
        if len(fields) > 50: fields = fields[:50] + ["..."]
        summary_lines.append(f"Coll: {col_name} [{', '.join(fields)}]")
    return "\n".join(summary_lines) if summary_lines else "No specific schemas found."
