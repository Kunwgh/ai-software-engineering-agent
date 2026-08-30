from app.rag.context import build_context


def test_build_context():
    results = [
        {
            "file_path": "app/database.py",
            "start_line": 1,
            "end_line": 5,
            "content": "def get_connection():\n    pass",
            "score": 0.95,
        },
        {
            "file_path": "app/repository.py",
            "start_line": 10,
            "end_line": 15,
            "content": "def get_user():\n    pass",
            "score": 0.80,
        },
    ]

    context = build_context(results)

    assert "app/database.py" in context
    assert "lines 1-5" in context
    assert "def get_connection()" in context

    assert "app/repository.py" in context
    assert "lines 10-15" in context
    assert "def get_user()" in context


def test_build_context_empty_results():
    context = build_context([])

    assert context == ""
