from chromadb import PersistentClient
from typing import List, Dict
import uuid

# Initialize Chroma DB (stores vectors locally)
chroma_client = PersistentClient(path="./backend/agent/chroma_db")

# Create a collection for Tarnished memories
collection_name = "tarnished_memories"
try:
    collection = chroma_client.get_collection(name=collection_name)
except ValueError:
    # Collection doesn't exist, create it
    collection = chroma_client.create_collection(name=collection_name)

# Simple embedding function using Ollama text embeddings
def get_embedding(text: str) -> List[float]:
    from app.core.ollama import get_embedding as ollama_get_embedding
    return ollama_get_embedding(text)

def add_memory(text: str, metadata: Dict = {}):
    vector = get_embedding(text)
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[str(uuid.uuid4())],
        embeddings=[vector]
    )

def query_memory(query: str, n_results: int = 3) -> List[Dict]:
    vector = get_embedding(query)
    results = collection.query(
        query_embeddings=[vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    return [
        {"document": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0], 
            results["metadatas"][0], 
            results["distances"][0]
        )
    ]

# Persist the database to disk
def persist():
    # With PersistentClient, data is automatically persisted
    pass
