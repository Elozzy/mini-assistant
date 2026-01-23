import requests
from typing import List
from app.core.config import OLLAMA_URL, OLLAMA_EMBEDDING_MODEL

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

def get_embedding(text: str) -> List[float]:
    """Get embedding vector from Ollama embeddings API."""
    # Construct embeddings URL from generate URL
    if OLLAMA_URL and "/api/generate" in OLLAMA_URL:
        embeddings_url = OLLAMA_URL.replace("/api/generate", "/api/embed")
    elif OLLAMA_URL:
        # If URL doesn't have /api/generate, assume it's a base URL
        embeddings_url = OLLAMA_URL.rstrip("/") + "/api/embed"
    else:
        # Default fallback
        embeddings_url = "http://localhost:11434/api/embed"
    
    try:
        response = requests.post(
            embeddings_url,
            json={
                "model": OLLAMA_EMBEDDING_MODEL,
                "input": text
            },
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Check for errors in response
        if "error" in result:
            error_msg = result.get("error", "Unknown error")
            raise ValueError(f"Ollama embedding error: {error_msg}. Make sure the model '{OLLAMA_EMBEDDING_MODEL}' is installed. Run: ollama pull {OLLAMA_EMBEDDING_MODEL}")
        
        # Ollama returns embeddings as an array, get the first one
        if "embeddings" not in result or not result["embeddings"]:
            raise ValueError(f"Invalid response from Ollama: missing embeddings. Response: {result}")
        
        return result["embeddings"][0]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(
                f"Ollama embedding model '{OLLAMA_EMBEDDING_MODEL}' not found. "
                f"Please install it by running: ollama pull {OLLAMA_EMBEDDING_MODEL}"
            ) from e
        raise
