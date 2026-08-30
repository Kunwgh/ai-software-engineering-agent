from pathlib import Path

from sympy import python

from app.rag.indexer import RepositoryIndexer
from app.rag.chunker import CodeChunker, CodeChunk 


def test_discover_files_ignores_unwanted_directories(tmp_path):
    repository = tmp_path

    (repository / "app").mkdir()
    (repository / ".venv").mkdir()
    (repository / ".git").mkdir()
    (repository / "__pycache__").mkdir()

    (repository / "app" / "main.py").write_text(
        "print('hello')"
    )

    (repository / ".venv" / "ignored.py").write_text(
        "ignored"
    )

    (repository / ".git" / "ignored.py").write_text(
        "ignored"
    )

    (repository / "__pycache__" / "ignored.pyc").write_text(
        "ignored"
    )

    (repository / "agent.db").write_text(
        "ignored"
    )

    indexer = RepositoryIndexer(str(repository))

    files = indexer.discover_files()

    relative_files = {
        path.relative_to(repository)
        for path in files
    }

    assert Path("app/main.py") in relative_files
    assert Path(".venv/ignored.py") not in relative_files
    assert Path(".git/ignored.py") not in relative_files
    assert Path("__pycache__/ignored.pyc") not in relative_files
    assert Path("agent.db") not in relative_files

def test_read_and_chunk_file(tmp_path):
    repository = tmp_path

    app_directory = repository / "app"
    app_directory.mkdir()

    file_path = app_directory / "main.py"

    file_path.write_text(
        "\n".join(f"line {i}" for i in range(1, 11)),
        encoding="utf-8",
    )

    chunker = CodeChunker(
        chunk_size=5,
        overlap=2,
    )

    indexer = RepositoryIndexer(
        str(repository),
        chunker=chunker,
    )

    chunks = indexer.read_and_chunk_file(file_path)

    assert len(chunks) == 3

    assert chunks[0].file_path == "app/main.py"
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 5

def test_embed_chunks(tmp_path):
    repository = tmp_path

    chunker = CodeChunker(
        chunk_size=5,
        overlap=2,
    )

    indexer = RepositoryIndexer(
        str(repository),
        chunker=chunker,
    )

    chunks = [
        CodeChunk(
            file_path="app/main.py",
            chunk_index=0,
            content="def hello():\n    print('hello')",
            start_line=1,
            end_line=2,
        ),
        CodeChunk(
            file_path="app/main.py",
            chunk_index=1,
            content="def goodbye():\n    print('bye')",
            start_line=3,
            end_line=4,
        ),
    ]

    embeddings = indexer.embed_chunks(chunks)

    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0
    assert len(embeddings[1]) > 0   

def test_save_chunks(tmp_path, monkeypatch):
    from app.database import database
    from app.database.schema import initialize_database
    from app.database.repository import get_code_chunks

    test_database = tmp_path / "test_agent.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    initialize_database()

    repository = tmp_path / "repository"
    repository.mkdir()

    indexer = RepositoryIndexer(str(repository))

    chunks = [
        CodeChunk(
            file_path="app/main.py",
            chunk_index=0,
            content="print('hello')",
            start_line=1,
            end_line=1,
        ),
        CodeChunk(
            file_path="app/main.py",
            chunk_index=1,
            content="print('world')",
            start_line=2,
            end_line=2,
        ),
    ]

    embeddings = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    chunk_ids = indexer.save_chunks(
        chunks,
        embeddings,
    )

    assert len(chunk_ids) == 2

    stored_chunks = get_code_chunks()

    assert len(stored_chunks) == 2
    assert stored_chunks[0]["file_path"] == "app/main.py"
    assert stored_chunks[0]["content"] == "print('hello')"
    assert stored_chunks[1]["content"] == "print('world')"


def test_index_repository(
    tmp_path,
    monkeypatch,
):
    from app.database import database
    from app.database.repository import get_code_chunks
    from app.database.schema import initialize_database

    test_database = tmp_path / "test_agent.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    initialize_database()

    repository = tmp_path / "repository"
    repository.mkdir()

    app_directory = repository / "app"
    app_directory.mkdir()

    file_path = app_directory / "main.py"

    file_path.write_text(
        "\n".join(
            [
                "def hello():",
                "    print('hello')",
                "",
                "def goodbye():",
                "    print('goodbye')",
            ]
        ),
        encoding="utf-8",
    )

    chunker = CodeChunker(
        chunk_size=3,
        overlap=1,
    )

    indexer = RepositoryIndexer(
        str(repository),
        chunker=chunker,
    )

    total_chunks = indexer.index_repository()

    assert total_chunks > 0

    stored_chunks = get_code_chunks()

    assert len(stored_chunks) == total_chunks

    assert stored_chunks[0]["file_path"] == "app/main.py"

    assert stored_chunks[0]["content"]
    assert stored_chunks[0]["embedding"]

