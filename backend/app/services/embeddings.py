from sentence_transformers import SentenceTransformer
import os
import dotenv
from typing import List, Tuple
import torch
from functools import lru_cache

dotenv.load_dotenv()

HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer('google/embeddinggemma-300m',
                              use_auth_token=HUGGING_FACE_TOKEN)

model = get_embedding_model()

def get_embedding(text: str) -> list[float]:
    embedding = model.encode([str(text)])
    return embedding[0].tolist()

def top_k_similar(search_query: str, memory_embeddings: list[dict], k: int = 3, threshold: float = 0) -> Tuple[List[int], List[float]]:
    query_embedding = get_embedding(search_query)
    query_embedding = torch.as_tensor(query_embedding).reshape(1, -1)

    k = min(k, len(memory_embeddings))

    similarity_scores = model.similarity(query_embedding, memory_embeddings).flatten()

    valid_indices = torch.where(similarity_scores >= threshold)[0]

    print("Similarity scores:", similarity_scores)

    print("Valid indices:", valid_indices)

    if len(valid_indices) == 0:
        return []

    sorted_descending = torch.argsort(similarity_scores[valid_indices], descending=True)
    sorted_indices = valid_indices[sorted_descending]
    top_k_indices = sorted_indices[:k]
    top_k_scores = similarity_scores[top_k_indices]

    return top_k_indices.tolist(), top_k_scores.tolist()