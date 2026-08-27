from pathlib import Path

from app.tools.repository import write_file


def test_write_file(tmp_path):
    result = write_file(
        str(tmp_path),
        "test_output.txt",
        "Hello from write_file",
    )

    output_file = Path(tmp_path) / "test_output.txt"

    assert output_file.exists()
    assert output_file.read_text() == "Hello from write_file"
    assert "Successfully wrote file" in result