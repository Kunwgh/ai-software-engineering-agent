from app.rag.chunker import CodeChunker

def test_chunk_text_creates_chunks():
    text = "\n".join(f"line {i}" for i in range(1, 11))

    chunker = CodeChunker(
        chunk_size=5,
        overlap=2,
    )

    chunks = chunker.chunk_text(
        file_path="example.py",
        text=text,
    )

    assert len(chunks) == 3

def test_chunk_metadata():
    text = "\n".join(f"line {i}" for i in range(1, 6))

    chunker = CodeChunker(
        chunk_size=5,
        overlap=2,
    )

    chunks = chunker.chunk_text(
        file_path="app/example.py",
        text=text,
    )

    chunk = chunks[0]

    assert chunk.file_path == "app/example.py"
    assert chunk.chunk_index == 0
    assert chunk.start_line == 1
    assert chunk.end_line == 5

def test_empty_text_returns_no_chunks():
    chunker = CodeChunker()

    chunks = chunker.chunk_text(
        file_path="empty.py",
        text="",
    )

    assert chunks == []

def test_invalid_chunk_size():
    try:
        CodeChunker(chunk_size=0)
        assert False
    except ValueError:
        pass

def test_invalid_overlap():
    try:
        CodeChunker(
            chunk_size=10,
            overlap=10,
        )
        assert False
    except ValueError:
        pass

def test_chunk_overlap():
    text = "\n".join(f"line {i}" for i in range(1, 11))

    chunker = CodeChunker(
        chunk_size=5,
        overlap=2,
    )

    chunks = chunker.chunk_text(
        file_path="example.py",
        text=text,
    )

    assert chunks[0].content == "line 1\nline 2\nline 3\nline 4\nline 5"
    assert chunks[1].content == "line 4\nline 5\nline 6\nline 7\nline 8"
    assert chunks[2].content == "line 7\nline 8\nline 9\nline 10"