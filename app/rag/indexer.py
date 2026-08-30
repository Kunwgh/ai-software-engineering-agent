from pathlib import Path
from app import embeddings
from app.rag.chunker import CodeChunk, CodeChunker
from app.embeddings.embedder import Embedder
from app.database.repository import create_code_chunk

DEFAULT_IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
}


DEFAULT_IGNORED_FILES = {
    "agent.db",
}


class RepositoryIndexer:
    def __init__(
    self,
    repository_path: str,
    chunker: CodeChunker | None = None,
    embedder: Embedder | None = None,
    ):
        self.repository_path = Path(repository_path).resolve()
        self.chunker = chunker or CodeChunker()
        self.embedder = embedder or Embedder()

    def discover_files(self) -> list[Path]:
        files = []

        for path in self.repository_path.rglob("*"):
            if not path.is_file():
                continue

            relative_parts = path.relative_to(
                self.repository_path
            ).parts

            if any(
                part in DEFAULT_IGNORED_DIRECTORIES
                for part in relative_parts
            ):
                continue

            if path.name in DEFAULT_IGNORED_FILES:
                continue

            files.append(path)

        return files

    def read_and_chunk_file(
        self,
        file_path: Path,
    ) -> list[CodeChunk]:
        try:
            text = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return []

        relative_path = file_path.relative_to(
            self.repository_path
        )

        return self.chunker.chunk_text(
           file_path=str(relative_path),
            text=text,
        )

    def embed_chunks(
        self,
        chunks: list[CodeChunk],
    ) -> list[list[float]]:
        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]

        return self.embedder.embed_many(texts)

    def save_chunks(
        self,
        chunks: list[CodeChunk],
        embeddings: list[list[float]],
    ) -> list[int]:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings"
            )

        chunk_ids = []

        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = create_code_chunk(
                file_path=chunk.file_path,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                embedding=embedding,
            )

            chunk_ids.append(chunk_id)

        return chunk_ids

    def index_repository(self) -> int:
        files = self.discover_files()

        total_chunks = 0

        for file_path in files:
            chunks = self.read_and_chunk_file(
                file_path
            )

            if not chunks:
                continue

            embeddings = self.embed_chunks(
                chunks
            )

            self.save_chunks(
                chunks,
                embeddings,
            )

            total_chunks += len(chunks)

        return total_chunks
