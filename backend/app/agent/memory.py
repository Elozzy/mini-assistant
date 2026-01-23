from typing import List, Dict

# Short-term memory (in-memory for now)
# Stores recent messages in this session
short_term_memory: List[Dict[str, str]] = []

def add_to_short_term(role: str, message: str):
    """
    role: 'user' or 'assistant'
    """
    short_term_memory.append({"role": role, "message": message})

def get_short_term_context(limit: int = 10) -> str:
    """
    Returns the last `limit` messages as a formatted string
    """
    context = ""
    for entry in short_term_memory[-limit:]:
        context += f"{entry['role'].upper()}: {entry['message']}\n"
    return context
