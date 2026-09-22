from langchain.tools import tool

from app.tools.executor import ToolExecutor


executor = ToolExecutor()


@tool
def lc_scan_repository(repository_path: str) -> str:
    """Scan a repository and return a list of source files."""
    return executor.execute(
        "scan_repository",
        {
            "repository_path": repository_path,
        },
    )


@tool
def lc_read_file(repository_path: str, file_path: str) -> str:
    """Read the contents of a file inside a repository."""
    return executor.execute(
        "read_file",
        {
            "repository_path": repository_path,
            "file_path": file_path,
        },
    )


@tool
def lc_write_file(
    repository_path: str,
    file_path: str,
    content: str,
) -> str:
    """Write or overwrite a file inside a repository."""
    return executor.execute(
        "write_file",
        {
            "repository_path": repository_path,
            "file_path": file_path,
            "content": content,
        },
    )


@tool
def lc_edit_file(
    repository_path: str,
    file_path: str,
    old_text: str,
    new_text: str,
) -> str:
    """Replace exact existing text in a repository file."""
    return executor.execute(
        "edit_file",
        {
            "repository_path": repository_path,
            "file_path": file_path,
            "old_text": old_text,
            "new_text": new_text,
        },
    )


@tool
def lc_run_command(
    repository_path: str,
    command: str,
) -> str:
    """Run a shell command inside the repository."""
    return executor.execute(
        "run_command",
        {
            "repository_path": repository_path,
            "command": command,
        },
    )


LANGCHAIN_TOOLS = [
    lc_scan_repository,
    lc_read_file,
    lc_write_file,
    lc_edit_file,
    lc_run_command,
]