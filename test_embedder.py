from app.embeddings.embedder import Embedder


def test_embed_returns_vector():
    embedder = Embedder()

    vector = embedder.embed("authentication function")

    assert isinstance(vector, list)
    assert len(vector) == 384


def test_embed_many_returns_vectors():
    embedder = Embedder()

    vectors = embedder.embed_many([
        "authentication function",
        "database connection",
    ])

    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert len(vectors[1]) == 384


def test_embed_rejects_empty_text():
    embedder = Embedder()

    try:
        embedder.embed("")
        assert False
    except ValueError:
        pass