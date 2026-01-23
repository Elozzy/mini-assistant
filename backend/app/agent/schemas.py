from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Action(BaseModel):
    tool: str
    device: str
    args: Dict[str, Any]

class AgentResponse(BaseModel):
    message: str
    actions: List[Action] = []
