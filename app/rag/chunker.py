from dataclasses import dataclass


@dataclass
class CodeChunk:
    file_path: str
    chunk_index: int
    content: str
    start_line: int
    end_line: int


class CodeChunker:
    def __init__(
        self,
        chunk_size: int = 50,
        overlap: int = 10,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(
        self,
        file_path: str,
        text: str,
    ) -> list[CodeChunk]:
        if not text.strip():
            return []

        lines = text.splitlines()

        step = self.chunk_size - self.overlap

        chunks = []

        for start in range(0, len(lines), step):
            end = min(start + self.chunk_size, len(lines))

            chunk_lines = lines[start:end]

            content = "\n".join(chunk_lines)

            chunks.append(
                CodeChunk(
                    file_path=file_path,
                    chunk_index=len(chunks),
                    content=content,
                    start_line=start + 1,
                    end_line=end,
                )
            )

            if end == len(lines):
                break

        return chunks


