from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class MongoAction(BaseModel):
    action: str
    collections: Optional[List[str]] = None
    collection: Optional[str] = None
    type: Optional[str] = "find"
    filter: Optional[Dict[str, Any]] = None
    pipeline: Optional[List[Dict[str, Any]]] = None
    projection: Optional[Dict[str, Any]] = None
