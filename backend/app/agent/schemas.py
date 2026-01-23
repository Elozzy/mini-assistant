from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Action(BaseModel):
    tool: str
    device: str
    args: Dict[str, Any]

class AgentResponse(BaseModel):
    message: str
    actions: List[Action] = []

# Tool definitions
TOOLS = [
    {
        "name": "filesystem.search",
        "description": "Search for files on a device",
        "parameters": {
            "extension": "pdf|txt|md",
            "sort": "last_modified",
            "limit": 1
        }
    },
    {
        "name": "filesystem.open",
        "description": "Open a file on a device",
        "parameters": {
            "path": "Full file path to open"
        }
    },
    {
        "name": "apps.open",
        "description": "Open an application on the device",
        "parameters": {
            "app_name": "Name of the application (e.g., VSCode, Safari)"
        }
    },
    {
        "name": "system.info",
        "description": "Fetch system information",
        "parameters": {}
    }
]
