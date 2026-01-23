# backend/app/api/chat.py

from fastapi import APIRouter
from pydantic import ValidationError
from app.core.ollama import generate
from app.agent.prompt import SYSTEM_PROMPT
from app.agent.schemas import AgentResponse
from app.agent.memory import add_to_short_term, get_short_term_context
import json
import re

router = APIRouter()
# Default device name for MacOS
DEFAULT_DEVICE = "MacBook Pro"

# safely parse JSON, even if Ollama adds extra text
def parse_json_safe(raw_output: str):
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise json.JSONDecodeError(
            "Could not parse JSON from LLM output",
            raw_output,
            0
        )

# ensure all actions have a device string
def ensure_device_fallback(actions: list):
    for action in actions:
        if not action.get("device"):
            action["device"] = DEFAULT_DEVICE
    return actions

@router.post("/chat")
def chat(payload: dict):
    """
    Chat endpoint for Tarnished.
    Expects:
    {
        "message": "User message here"
    }
    Returns structured AgentResponse:
    {
        "message": "Friendly summary",
        "actions": [
            {
                "tool": "tool_name",
                "device": "device_name",
                "args": {...}
            }
        ]
    }
    """
    user_message = payload.get("message", "")

    # Add user message to short-term memory
    add_to_short_term("user", user_message)

    # Build prompt for Ollama
    short_term_context = get_short_term_context()
    prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_message}
"""

    # Call Ollama to generate response
    raw_output = generate(prompt)
    try:

        data = parse_json_safe(raw_output)
        # Ensure device field is always present
        data["actions"] = ensure_device_fallback(data.get("actions", []))
        # Add assistant message to short-term memory
        add_to_short_term("assistant", data["message"])
        # Validate with Pydantic schema
        agent_response = AgentResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        # Return helpful debug info if parsing fails
        return {
            "error": "Invalid LLM output",
            "raw_output": raw_output,
            "details": str(e)
        }

    # Return validated response with short-term context
    return {
        "response": agent_response.dict(),
        "context": get_short_term_context()
    }
