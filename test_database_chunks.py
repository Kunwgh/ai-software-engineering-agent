import json

import app.database.database as database
from app.database.schema import initialize_database
from app.database.repository import (
    create_code_chunk,
    get_code_chunks,
)


def test_create_and_get_code_chunk(tmp_path, monkeypatch):
    test_database = tmp_path / "test_agent.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    initialize_database()

    embedding = [0.1, 0.2, 0.3]

    chunk_id = create_code_chunk(
        file_path="app/auth.py",
        chunk_index=0,
        content="def login():\n    pass",
        start_line=1,
        end_line=2,
        embedding=embedding,
    )

    chunks = get_code_chunks()

    assert chunk_id == 1
    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk["file_path"] == "app/auth.py"
    assert chunk["chunk_index"] == 0
    assert chunk["content"] == "def login():\n    pass"
    assert chunk["start_line"] == 1
    assert chunk["end_line"] == 2

    stored_embedding = json.loads(chunk["embedding"])

    assert stored_embedding == embedding
