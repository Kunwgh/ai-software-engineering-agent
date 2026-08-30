import json
import math

from app.database.repository import get_code_chunks
from app.embeddings.embedder import Embedder


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have the same dimensions"
        )

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


class Retriever:
    def __init__(
        self,
        embedder: Embedder | None = None,
    ):
        self.embedder = embedder or Embedder()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ):
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0"
            )

        if not 0.0 <= min_score <= 1.0:
            raise ValueError(
                "min_score must be between 0.0 and 1.0"
            )

        query_embedding = self.embedder.embed(query)

        stored_chunks = get_code_chunks()

        results = []

        for chunk in stored_chunks:
            embedding = json.loads(
                chunk["embedding"]
            )

            score = cosine_similarity(
                query_embedding,
                embedding,
            )

            if score < min_score:
                    continue
            
            results.append(
                {
                    "id": chunk["id"],
                    "file_path": chunk["file_path"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "score": score,
                }
            )

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]