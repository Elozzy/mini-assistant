import requests
from app.core.config import OLLAMA_URL

def generate(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()
    return response.json()["response"]
