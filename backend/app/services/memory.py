from app.services.embeddings import get_embedding, top_k_similar
import os
import dotenv
import json
import torch
from uuid import uuid4 

dotenv.load_dotenv()
MEMORY_FILE_PATH = os.getenv("MEMORY_FILE_PATH")

class MemoryService:
    def __init__(self):
        pass

    def retrieve_memory(self, search_query: str, k: int = 3, threshold: float = 0.4):
        with open(MEMORY_FILE_PATH, "r") as f:
            memories = json.load(f)

        memory_embeddings = [memory["embedding"] for memory in memories if "embedding" in memory]
        if not memory_embeddings:
            return []

        top_k_indices, top_k_scores = top_k_similar(search_query, memory_embeddings, k, threshold)

        relevant_memories = [memories[i] for i in top_k_indices]

        for memory in relevant_memories:
            memory["similarity_score"] = top_k_scores[relevant_memories.index(memory)]
            del memory["embedding"]

        return relevant_memories

    def save_memory(self, category: str, tags: list, content: str):
        new_memory = {
            "id": str(uuid4()),
            "category": category,
            "tags": tags,
            "content": content,
            "embedding": get_embedding(content)
        }

        if os.path.exists(MEMORY_FILE_PATH):
            with open(MEMORY_FILE_PATH, "r") as f:
                memories = json.load(f)
        else:
            memories = []

        memories.append(new_memory)

        with open(MEMORY_FILE_PATH, "w") as f:
            json.dump(memories, f, indent=2)