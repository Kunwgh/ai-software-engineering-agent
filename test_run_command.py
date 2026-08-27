import pytest

from app.tools.repository import run_command


def test_run_command():
    result = run_command(
        ".",
        "python --version",
    )

    assert "Exit code: 0" in result
    assert "Python 3.14.6" in result


def test_run_command_rejects_unknown_command():
    with pytest.raises(ValueError, match="is not allowed"):
        run_command(
            ".",
            "rm test_file.txt",
        )


def test_run_command_rejects_shell_operators():
    with pytest.raises(ValueError, match="Shell operators"):
        run_command(
            ".",
            "python --version && ls",
        )


def test_run_command_rejects_pipe():
    with pytest.raises(ValueError, match="Shell operators"):
        run_command(
            ".",
            "python --version | cat",
        )