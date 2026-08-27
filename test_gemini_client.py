from app.llm.gemini_client import GeminiClient


def test_create_interaction(monkeypatch):
    gemini = GeminiClient()

    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return "fake-response"

    monkeypatch.setattr(
        gemini.client.interactions,
        "create",
        fake_create,
    )

    result = gemini.create_interaction(
        "Inspect the repository.",
        [{"type": "function", "name": "scan_repository"}],
    )

    assert result == "fake-response"

    assert captured["model"] == "gemini-3.6-flash"
    assert captured["input"] == "Inspect the repository."
    assert captured["tools"] == [
        {"type": "function", "name": "scan_repository"}
    ]


def test_continue_interaction(monkeypatch):
    gemini = GeminiClient()

    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return "fake-response"

    monkeypatch.setattr(
        gemini.client.interactions,
        "create",
        fake_create,
    )

    function_results = [
        {
            "type": "function_result",
            "call_id": "call-1",
            "name": "read_file",
            "result": "file contents",
        }
    ]

    result = gemini.continue_interaction(
        "interaction-123",
        function_results,
    )

    assert result == "fake-response"

    assert captured["model"] == "gemini-3.6-flash"
    assert captured["previous_interaction_id"] == "interaction-123"
    assert captured["input"] == function_results