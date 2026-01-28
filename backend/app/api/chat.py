from fastapi import APIRouter
from pydantic import ValidationError
from app.core.ollama import generate
from app.agent.prompt import SYSTEM_PROMPT
from app.agent.schemas import AgentResponse
from app.agent.memory import add_to_short_term, get_short_term_context
import json
import re
from app.agent.long_term_memory import add_memory, query_memory, persist
import requests
router = APIRouter()
# Default device name for MacOS
DEFAULT_DEVICE = "MacBook Pro"
AGENT_URL = "http://localhost:8081/execute" 

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

def execute_actions_on_agent(actions: list) -> list:
    """Send actions to MacOS agent and return results"""
    if not actions:
        return []

    # Convert Pydantic models to dictionaries for JSON serialization
    def to_dict(action):
        if hasattr(action, 'model_dump'):  # Pydantic v2
            return action.model_dump()
        elif hasattr(action, 'dict'):  # Pydantic v1
            return action.dict()
        elif isinstance(action, dict):
            return action
        else:
            # Fallback: try to access attributes
            return {
                "tool": getattr(action, 'tool', ''),
                "device": getattr(action, 'device', ''),
                "args": getattr(action, 'args', {})
            }
    
    actions_dict = [to_dict(action) for action in actions]
    payload = {"actions": actions_dict}
    try:
        response = requests.post(AGENT_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException as e:
        # If agent is down, return error for each action
        return [
            {
                "tool": a.tool if hasattr(a, 'tool') else (a.get("tool", "") if isinstance(a, dict) else ""),
                "device": a.device if hasattr(a, 'device') else (a.get("device", "") if isinstance(a, dict) else ""),
                "status": f"Agent error: {str(e)}",
                "output": ""
            }
            for a in actions
        ]


@router.post("/chat")
def chat(payload: dict):
    user_message = payload.get("message", "")

    # Add user message to short-term memory
    add_to_short_term("user", user_message)

    # Query long-term memory for relevant context
    retrieved_memories = query_memory(user_message, n_results=3)
    memory_context = ""
    for mem in retrieved_memories:
        memory_context += f"PAST MEMORY: {mem['document']}\n"

    # Include short-term + long-term memory in prompt
    short_term_context = get_short_term_context()
    prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{short_term_context}

Relevant past memories:
{memory_context}

User message:
{user_message}
"""

    try:
        raw_output = generate(prompt)
    except ConnectionError as e:
        return {
            "error": "Ollama connection failed",
            "message": str(e),
            "details": "Make sure Ollama is running: ollama serve"
        }

    try:
        data = parse_json_safe(raw_output)
        data["actions"] = ensure_device_fallback(data.get("actions", []))
        agent_response = AgentResponse(**data)

        # Add AI response to short-term memory
        add_to_short_term("assistant", agent_response.message)

        # Optionally add important memories to long-term memory
        add_memory(user_message, metadata={"role": "user"})
        add_memory(agent_response.message, metadata={"role": "assistant"})
        # Persist vector store
        persist()
        # --- EXECUTE ACTIONS ON MACOS AGENT ---
        execution_results = execute_actions_on_agent(agent_response.actions)

        # Include execution results in response
        response = agent_response.dict()
        response["execution_results"] = execution_results

    except (json.JSONDecodeError, ValidationError) as e:
        return {
            "error": "Invalid LLM output",
            "raw_output": raw_output,
            "details": str(e)
        }
    
    return response