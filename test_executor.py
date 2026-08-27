from app.tools.executor import ToolExecutor
import pytest


def test_read_file():
    executor = ToolExecutor()

    result = executor.execute(
        "read_file",
        {
            "repository_path": ".",
            "file_path": "app/agents/agent.py",
        },
    )

    assert "class SoftwareEngineeringAgent" in result

def test_unknown_tool():
    executor = ToolExecutor()

    try:
        executor.execute("does_not_exist", {})
        assert False
    except ValueError as error:
        assert "Unknown tool" in str(error)


def test_missing_required_argument():
    executor = ToolExecutor()

    try:
        executor.execute(
            "edit_file",
            {
                "repository_path": ".",
                "file_path": "test_tools.py",
                "new_text": "hello",
            },
        )
        assert False
    except ValueError as error:
        assert "old_text" in str(error)

def test_write_file(tmp_path):
    executor = ToolExecutor()

    result = executor.execute(
        "write_file",
        {
            "repository_path": str(tmp_path),
            "file_path": "example.txt",
            "content": "Hello Agent",
        },
    )

    assert "Successfully wrote file" in result

    created_file = tmp_path / "example.txt"

    assert created_file.exists()
    assert created_file.read_text() == "Hello Agent"


def test_edit_file(tmp_path):
    executor = ToolExecutor()

    file_path = tmp_path / "example.txt"
    file_path.write_text("Hello Agent")

    result = executor.execute(
        "edit_file",
        {
            "repository_path": str(tmp_path),
            "file_path": "example.txt",
            "old_text": "Hello Agent",
            "new_text": "Hello Software Engineering Agent",
        },
    )

    assert "Successfully edited" in result
    assert file_path.read_text() == "Hello Software Engineering Agent"

def test_run_command():
    executor = ToolExecutor()

    result = executor.execute(
        "run_command",
        {
            "repository_path": ".",
            "command": "python --version",
        },
    )

    assert "Python" in result
    assert "Exit code: 0" in result

def test_all_tools_are_registered():
    from app.tools.registry import TOOLS

    expected_tools = {
        "scan_repository",
        "read_file",
        "write_file",
        "edit_file",
        "run_command",
    }

    assert set(TOOLS.keys()) == expected_tools

def test_unexpected_argument():
    executor = ToolExecutor()

    with pytest.raises(ValueError, match="Unexpected argument"):
        executor.execute(
            "read_file",
            {
                "repository_path": ".",
                "file_path": "app/agents/agent.py",
                "unexpected": "value",
            },
        )