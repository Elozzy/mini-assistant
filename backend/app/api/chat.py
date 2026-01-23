from fastapi import APIRouter
from pydantic import ValidationError
from app.core.ollama import generate
from app.agent.prompt import SYSTEM_PROMPT
from app.agent.schemas import AgentResponse
from app.agent.memory import add_to_short_term, get_short_term_context
import json
import re
from app.agent.long_term_memory import add_memory, query_memory, persist

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

    raw_output = generate(prompt)

    try:
        data = parse_json_safe(raw_output)
        data["actions"] = ensure_device_fallback(data.get("actions", []))
        agent_response = AgentResponse(**data)

        # Add AI response to short-term memory
        add_to_short_term("assistant", agent_response.message)

        # Optionally add important memories to long-term memory
        add_memory(user_message, metadata={"role": "user"})
        add_memory(agent_response.message, metadata={"role": "assistant"})

    except (json.JSONDecodeError, ValidationError) as e:
        return {
            "error": "Invalid LLM output",
            "raw_output": raw_output,
            "details": str(e)
        }

    # Persist vector store
    persist()

    return {
        "response": agent_response.dict(),
        "context": get_short_term_context()
    }