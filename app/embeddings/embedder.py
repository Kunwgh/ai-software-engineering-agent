from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Text cannot be empty")

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
        )

        return embedding.tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            raise ValueError("Texts cannot be empty")

        if any(not text.strip() for text in texts):
            raise ValueError("Texts cannot contain empty strings")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
        )

        return embeddings.tolist()