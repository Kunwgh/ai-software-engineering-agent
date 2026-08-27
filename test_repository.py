from app.tools.repository import scan_repository


def test_scan_repository():
    files = scan_repository(".")

    assert isinstance(files, list)
    assert "app/agents/agent.py" in files
    assert "app/tools/repository.py" in files