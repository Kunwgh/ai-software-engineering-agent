from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}

IGNORED_FILES = {
    ".env",
    ".DS_Store",
}


def scan_repository(repository_path: str) -> list[str]:
    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {root}"
        )

    files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.name in IGNORED_FILES:
            continue

        if any(
            ignored in path.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue

        files.append(str(path.relative_to(root)))

    return sorted(files)

def read_file(repository_path: str, file_path: str) -> str:
    root = Path(repository_path).resolve()
    target = (root / file_path).resolve()

    if not target.exists():
        raise FileNotFoundError(
            f"File does not exist: {file_path}"
        )

    if not target.is_file():
        raise IsADirectoryError(
            f"Path is not a file: {file_path}"
        )

    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError(
            "File path must stay inside the repository"
        )

    return target.read_text(encoding="utf-8")