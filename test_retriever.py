import pytest

from app.database import database
from app.database.repository import create_code_chunk
from app.database.schema import initialize_database
from app.rag.retriever import Retriever, cosine_similarity


def test_cosine_similarity_identical_vectors():
    result = cosine_similarity(
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
    )

    assert result == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    result = cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    )

    assert result == pytest.approx(0.0)


def test_cosine_similarity_opposite_vectors():
    result = cosine_similarity(
        [1.0, 0.0],
        [-1.0, 0.0],
    )

    assert result == pytest.approx(-1.0)


def test_cosine_similarity_rejects_different_dimensions():
    with pytest.raises(ValueError):
        cosine_similarity(
            [1.0, 2.0],
            [1.0, 2.0, 3.0],
        )


def test_cosine_similarity_zero_vector():
    result = cosine_similarity(
        [0.0, 0.0],
        [1.0, 2.0],
    )

    assert result == 0.0


class FakeEmbedder:
    def embed(self, text):
        return [1.0, 0.0, 0.0]


def test_retrieve_returns_most_similar_chunks(
    tmp_path,
    monkeypatch,
):
    test_database = tmp_path / "test_agent.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    initialize_database()

    create_code_chunk(
        file_path="app/database.py",
        chunk_index=0,
        content="database connection",
        start_line=1,
        end_line=2,
        embedding=[1.0, 0.0, 0.0],
    )

    create_code_chunk(
        file_path="app/auth.py",
        chunk_index=0,
        content="authentication code",
        start_line=1,
        end_line=2,
        embedding=[0.0, 1.0, 0.0],
    )

    create_code_chunk(
        file_path="app/repository.py",
        chunk_index=0,
        content="database repository",
        start_line=1,
        end_line=2,
        embedding=[0.8, 0.6, 0.0],
    )

    retriever = Retriever(
        embedder=FakeEmbedder(),
    )

    results = retriever.retrieve(
        "database connection",
        top_k=2,
    )

    assert len(results) == 2

    assert results[0]["file_path"] == "app/database.py"
    assert results[0]["score"] == pytest.approx(1.0)

    assert results[1]["file_path"] == "app/repository.py"

def test_retrieve_filters_low_similarity_chunks(
    tmp_path,
    monkeypatch,
):
    test_database = tmp_path / "test_agent.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    initialize_database()

    create_code_chunk(
        file_path="app/relevant.py",
        chunk_index=0,
        content="relevant code",
        start_line=1,
        end_line=2,
        embedding=[1.0, 0.0, 0.0],
    )

    create_code_chunk(
        file_path="app/irrelevant.py",
        chunk_index=0,
        content="irrelevant code",
        start_line=1,
        end_line=2,
        embedding=[0.0, 1.0, 0.0],
    )

    retriever = Retriever(
        embedder=FakeEmbedder(),
    )

    results = retriever.retrieve(
        "database connection",
        top_k=5,
        min_score=0.5,
    )

    assert len(results) == 1

    assert results[0]["file_path"] == "app/relevant.py"
    assert results[0]["score"] == pytest.approx(1.0)