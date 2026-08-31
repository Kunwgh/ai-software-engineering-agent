from mcp.server import MCPServer

from app.tools.repository import (
    scan_repository,
    read_file,
    write_file,
    edit_file,
    run_command,
)


mcp = MCPServer("AI Software Engineering Agent")


@mcp.tool()
def scan_repository_tool(repository_path: str) -> list[str]:
    """Scan a repository and return its file paths."""
    return scan_repository(repository_path)


@mcp.tool()
def read_file_tool(
    repository_path: str,
    file_path: str,
) -> str:
    """Read a file from a repository."""
    return read_file(repository_path, file_path)


@mcp.tool()
def write_file_tool(
    repository_path: str,
    file_path: str,
    content: str,
) -> str:
    """Create or overwrite a file in a repository."""
    return write_file(repository_path, file_path, content)


@mcp.tool()
def edit_file_tool(
    repository_path: str,
    file_path: str,
    old_text: str,
    new_text: str,
) -> str:
    """Replace the first occurrence of text in a repository file."""
    return edit_file(
        repository_path,
        file_path,
        old_text,
        new_text,
    )


@mcp.tool()
def run_command_tool(
    repository_path: str,
    command: str,
) -> str:
    """Run a shell command inside the repository."""
    return run_command(repository_path, command)


if __name__ == "__main__":
    mcp.run()