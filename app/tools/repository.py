from pathlib import Path
import subprocess
import shlex


ALLOWED_COMMANDS = {
    "python",
    "pytest",
    "git",
    "ls",
    "pwd",
    "cat",
    "find",
    "grep",
    "head",
    "tail",
}


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

def write_file(
    repository_path: str,
    file_path: str,
    content: str,
) -> str:
    root = Path(repository_path).resolve()
    target = (root / file_path).resolve()

    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError(
            "File path must stay inside the repository"
        )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        content,
        encoding="utf-8",
    )

    return f"Successfully wrote file: {file_path}"

def edit_file(
    repository_path: str,
    file_path: str,
    old_text: str,
    new_text: str,
) -> str:
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

    content = target.read_text(encoding="utf-8")

    if old_text not in content:
        raise ValueError(
            f"Text to replace was not found in file: {file_path}"
        )

    updated_content = content.replace(old_text, new_text, 1)

    target.write_text(updated_content, encoding="utf-8")

    return f"Successfully edited {file_path}"

def run_command(
    repository_path: str,
    command: str,
) -> str:
    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {root}"
        )

    try:
        parts = shlex.split(command)
    except ValueError as exc:
        raise ValueError(
            f"Invalid command syntax: {exc}"
        )

    if not parts:
        raise ValueError("Command cannot be empty")

    executable = parts[0]

    if executable not in ALLOWED_COMMANDS:
        raise ValueError(
            f"Command '{executable}' is not allowed"
        )

    dangerous_tokens = {
        ";",
        "&&",
        "||",
        "|",
        ">",
        ">>",
        "<",
        "$(",
        "`",
    }

    if any(
        token in command
        for token in dangerous_tokens
    ):
        raise ValueError(
            "Shell operators are not allowed"
        )

    result = subprocess.run(
        parts,
        cwd=root,
        capture_output=True,
        text=True,
    )

    output = result.stdout

    if result.stderr:
        output += "\n" + result.stderr

    return (
        f"Exit code: {result.returncode}\n"
        f"Output:\n{output}"
    )