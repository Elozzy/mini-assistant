from fastapi import APIRouter
from app.core.ollama import generate
from app.agent.prompt import SYSTEM_PROMPT

router = APIRouter()

@router.post("/chat")
def chat(payload: dict):
    user_message = payload.get("message", "")

    prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_message}
"""

    output = generate(prompt)

    return {
        "raw_output": output
    }
