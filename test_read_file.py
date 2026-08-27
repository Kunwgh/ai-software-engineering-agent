from app.tools.repository import read_file


def test_read_file():
    content = read_file(
        ".",
        "app/agents/agent.py",
    )

    assert isinstance(content, str)
    assert len(content) > 0
    assert "class SoftwareEngineeringAgent" in content