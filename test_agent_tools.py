from app.agents.agent import SoftwareEngineeringAgent
import pytest

def test_use_tool():
    agent = SoftwareEngineeringAgent()

    result = agent.use_tool(
        "read_file",
        {
            "repository_path": ".",
            "file_path": "app/agents/agent.py",
        },
    )

    assert isinstance(result, str)
    assert "class SoftwareEngineeringAgent" in result


def test_get_gemini_tools():
    agent = SoftwareEngineeringAgent()

    tools = agent._get_gemini_tools()

    assert isinstance(tools, list)
    assert len(tools) == 5

    tool_names = {tool["name"] for tool in tools}

    assert tool_names == {
        "scan_repository",
        "read_file",
        "write_file",
        "edit_file",
        "run_command",
    }


def test_read_file_gemini_schema():
    agent = SoftwareEngineeringAgent()

    tools = agent._get_gemini_tools()

    read_file_tool = next(
        tool for tool in tools
        if tool["name"] == "read_file"
    )

    assert read_file_tool["type"] == "function"

    assert "repository_path" in read_file_tool["parameters"]["properties"]
    assert "file_path" in read_file_tool["parameters"]["properties"]

    assert read_file_tool["parameters"]["required"] == [
        "repository_path",
        "file_path",
    ]

def test_run_rejects_zero_max_iterations():
    agent = SoftwareEngineeringAgent()

    with pytest.raises(ValueError, match="max_iterations must be greater than 0"):
        agent.run("test task", max_iterations=0)


def test_run_rejects_negative_max_iterations():
    agent = SoftwareEngineeringAgent()

    with pytest.raises(ValueError, match="max_iterations must be greater than 0"):
        agent.run("test task", max_iterations=-1)

def test_run_enforces_max_iterations(monkeypatch):
    agent = SoftwareEngineeringAgent()

    class FakeResponse:
        id = "fake-response-id"
        output_text = ""

        steps = [
            type(
                "FakeFunctionCall",
                (),
                {
                    "type": "function_call",
                    "name": "scan_repository",
                    "arguments": {"repository_path": "."},
                    "id": "fake-call-id",
                },
            )()
        ]

    def fake_create(**kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        agent.llm.client.interactions,
        "create",
        fake_create,
    )

    with pytest.raises(
        RuntimeError,
        match="Agent exceeded maximum iterations: 2",
    ):
        agent.run("test task", max_iterations=2)

def test_run_recovers_from_tool_failure(monkeypatch):
    agent = SoftwareEngineeringAgent()

    class FakeFunctionCall:
        type = "function_call"
        name = "read_file"
        arguments = {
            "repository_path": ".",
            "file_path": "missing_file.py",
        }
        id = "fake-call-id"

    class FakeResponse:
        id = "fake-response-id"
        output_text = "Recovered from tool failure."

        def __init__(self, steps):
            self.steps = steps

    responses = [
        FakeResponse([FakeFunctionCall()]),
        FakeResponse([]),
    ]

    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    def fake_execute(tool_name, arguments):
        raise FileNotFoundError("File does not exist")

    monkeypatch.setattr(
        agent.llm.client.interactions,
        "create",
        fake_create,
    )

    monkeypatch.setattr(
        agent.tool_executor,
        "execute",
        fake_execute,
    )

    result = agent.run(
        "Read the missing file.",
        max_iterations=2,
    )

    assert result == "Recovered from tool failure."

    assert len(calls) == 2

    function_results = calls[1]["input"]

    assert function_results[0]["type"] == "function_result"
    assert function_results[0]["call_id"] == "fake-call-id"
    assert function_results[0]["name"] == "read_file"
    assert "Tool execution failed" in function_results[0]["result"]
    assert "File does not exist" in function_results[0]["result"]

def test_run_handles_multiple_tool_calls(monkeypatch):
    agent = SoftwareEngineeringAgent()

    class FakeFunctionCall:
        type = "function_call"

        def __init__(self, name, arguments, call_id):
            self.name = name
            self.arguments = arguments
            self.id = call_id

    class FakeResponse:
        output_text = "Completed multiple tools."
        
        def __init__(self, response_id, steps):
            self.id = response_id
            self.steps = steps

    first_response = FakeResponse(
        "response-1",
        [
            FakeFunctionCall(
                "read_file",
                {
                    "repository_path": ".",
                    "file_path": "test_tools.py",
                },
                "call-1",
            ),
            FakeFunctionCall(
                "scan_repository",
                {
                    "repository_path": ".",
                },
                "call-2",
            ),
        ],
    )

    final_response = FakeResponse(
        "response-2",
        [],
    )

    responses = [first_response, final_response]

    executed_tools = []

    def fake_create(**kwargs):
        return responses.pop(0)

    def fake_execute(tool_name, arguments):
        executed_tools.append((tool_name, arguments))
        return f"Result from {tool_name}"

    monkeypatch.setattr(
        agent.llm.client.interactions,
        "create",
        fake_create,
    )

    monkeypatch.setattr(
        agent.tool_executor,
        "execute",
        fake_execute,
    )

    result = agent.run(
        "Read a file and scan the repository.",
        max_iterations=2,
    )

    assert result == "Completed multiple tools."

    assert executed_tools == [
        (
            "read_file",
            {
                "repository_path": ".",
                "file_path": "test_tools.py",
            },
        ),
        (
            "scan_repository",
            {
                "repository_path": ".",
            },
        ),
    ]

def test_run_sends_tool_results_back_to_gemini(monkeypatch):
    agent = SoftwareEngineeringAgent()

    class FakeFunctionCall:
        type = "function_call"
        name = "read_file"
        arguments = {
            "repository_path": ".",
            "file_path": "test_tools.py",
        }
        id = "call-123"

    class FakeResponse:
        def __init__(self, response_id, steps, output_text=""):
            self.id = response_id
            self.steps = steps
            self.output_text = output_text

    responses = [
        FakeResponse(
            "response-1",
            [FakeFunctionCall()],
        ),
        FakeResponse(
            "response-2",
            [],
            "Tool result received.",
        ),
    ]

    captured_calls = []

    def fake_create(**kwargs):
        captured_calls.append(kwargs)
        return responses.pop(0)

    def fake_execute(tool_name, arguments):
        return "Contents of test_tools.py"

    monkeypatch.setattr(
        agent.llm.client.interactions,
        "create",
        fake_create,
    )

    monkeypatch.setattr(
        agent.tool_executor,
        "execute",
        fake_execute,
    )

    result = agent.run(
        "Read test_tools.py.",
        max_iterations=2,
    )

    assert result == "Tool result received."

    assert len(captured_calls) == 2

    second_call = captured_calls[1]

    assert second_call["previous_interaction_id"] == "response-1"

    assert second_call["input"] == [
        {
            "type": "function_result",
            "call_id": "call-123",
            "name": "read_file",
            "result": "Contents of test_tools.py",
        }
    ]