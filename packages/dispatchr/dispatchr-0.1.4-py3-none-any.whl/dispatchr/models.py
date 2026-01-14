from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class AgentRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = {}

class AgentResponse(BaseModel):
    response: str
    reflection: str
    sources: List[str] = []