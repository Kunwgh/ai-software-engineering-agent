from pathlib import Path

from app.tools.repository import edit_file, write_file


def test_edit_file(tmp_path):
    write_file(
        str(tmp_path),
        "test_output.txt",
        "Hello from write_file",
    )

    result = edit_file(
        str(tmp_path),
        "test_output.txt",
        "Hello from write_file",
        "Hello from edit_file",
    )

    output_file = Path(tmp_path) / "test_output.txt"

    assert output_file.read_text() == "Hello from edit_file"
    assert "Successfully edited" in result