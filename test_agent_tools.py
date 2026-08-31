from app.agents.agent import SoftwareEngineeringAgent
import pytest

class FakeRetriever:
    def retrieve(self, query, top_k=5):
        return []


def test_agent_accepts_retriever():
    retriever = FakeRetriever()

    agent = SoftwareEngineeringAgent(
        retriever=retriever,
    )

    assert agent.retriever is retriever

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
    agent = SoftwareEngineeringAgent(
        retriever=FakeRetriever(),
    )

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
    agent = SoftwareEngineeringAgent(
        retriever=FakeRetriever(),
)

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
    agent = SoftwareEngineeringAgent(
    retriever=FakeRetriever(),
    )

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
    agent = SoftwareEngineeringAgent(
        retriever=FakeRetriever(),
    )

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

def test_agent_retrieves_context():
    class FakeRetriever:
        def retrieve(self, query, top_k=5, min_score=0.0):
            assert query == "Where is the database connection?"
            assert top_k == 3
            assert min_score == 0.0

            return [
                {
                    "file_path": "app/database.py",
                    "content": "database connection",
                    "start_line": 10,
                    "end_line": 20,
                    "score": 1.0,
                }
            ]

    retriever = FakeRetriever()

    agent = SoftwareEngineeringAgent(
        retriever=retriever,
    )

    context = agent.retrieve_context(
        "Where is the database connection?",
        top_k=3,
    )

    assert context == (
        "--- app/database.py (lines 10-20) ---\n"
        "database connection"
    )

def test_build_task_prompt_includes_rag_context():
    class FakeRetriever:
        def retrieve(self, query, top_k=5, min_score=0.0):
            assert query == "Where is the database connection?"
            assert top_k == 5

            return [
                {
                    "file_path": "app/database.py",
                    "content": "connection = sqlite3.connect(...)",
                    "start_line": 10,
                    "end_line": 10,
                    "score": 1.0,
                }
            ]

    agent = SoftwareEngineeringAgent(
        retriever=FakeRetriever(),
    )

    prompt = agent._build_task_prompt(
        "Where is the database connection?"
    )

    assert "REPOSITORY CONTEXT:" in prompt
    assert "app/database.py" in prompt
    assert "connection = sqlite3.connect(...)" in prompt
    assert "Where is the database connection?" in prompt

def test_build_task_prompt_without_context_returns_task():
    class FakeRetriever:
        def retrieve(self, query, top_k=5, min_score=0.0):
            return []

    agent = SoftwareEngineeringAgent(
        retriever=FakeRetriever(),
    )

    task = "Explain this project."

    prompt = agent._build_task_prompt(task)

    assert prompt == task

def test_run_sends_rag_context_to_gemini(monkeypatch):
    class FakeRetriever:
        def retrieve(self, query, top_k=5, min_score=0.0):
            return [
                {
                    "file_path": "app/database.py",
                    "content": "connection = sqlite3.connect('agent.db')",
                    "start_line": 10,
                    "end_line": 10,
                    "score": 1.0,
                }
            ]

    agent = SoftwareEngineeringAgent(
        retriever=FakeRetriever(),
    )

    class FakeResponse:
        id = "response-1"
        steps = []
        output_text = "The database connection is created in app/database.py."

    captured_calls = []

    def fake_create(**kwargs):
        captured_calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr(
        agent.llm.client.interactions,
        "create",
        fake_create,
    )

    result = agent.run(
        "Where is the database connection created?",
        max_iterations=2,
    )

    assert result == (
        "The database connection is created in app/database.py."
    )

    assert len(captured_calls) == 1

    prompt = captured_calls[0]["input"]

    assert "REPOSITORY CONTEXT:" in prompt
    assert "app/database.py" in prompt
    assert "connection = sqlite3.connect('agent.db')" in prompt
    assert "Where is the database connection created?" in prompt

def test_build_task_prompt_continues_when_rag_fails():
    class FailingRetriever:
        def retrieve(self, query, top_k=5, min_score=0.0):
            raise RuntimeError("RAG unavailable")

    agent = SoftwareEngineeringAgent(
        retriever=FailingRetriever(),
    )

    task = "Explain the database connection."

    prompt = agent._build_task_prompt(task)

    assert prompt == task

def test_build_task_prompt_passes_min_score_to_retriever():
    class FakeRetriever:
        def __init__(self):
            self.received_min_score = None

        def retrieve(self, query, top_k=5, min_score=0.0):
            self.received_min_score = min_score
            return []

    retriever = FakeRetriever()

    agent = SoftwareEngineeringAgent(
        retriever=retriever,
    )

    task = "Explain the database connection."

    agent._build_task_prompt(
        task,
        top_k=3,
        min_score=0.6,
    )

    assert retriever.received_min_score == 0.6

def test_run_uses_rag_enriched_prompt():
    class FakeRetriever:
        def retrieve(self, query, top_k=5, min_score=0.0):
            return [
                {
                    "file_path": "app/database.py",
                    "content": "DATABASE_URL = 'sqlite:///agent.db'",
                    "start_line": 1,
                    "end_line": 1,
                    "score": 1.0,
                }
            ]

    agent = SoftwareEngineeringAgent(
        retriever=FakeRetriever(),
    )

    class FakeResponse:
        id = "response-1"
        steps = []
        output_text = "The database uses SQLite."

    captured_calls = []

    def fake_create(**kwargs):
        captured_calls.append(kwargs)
        return FakeResponse()

    agent.llm.client.interactions.create = fake_create

    result = agent.run(
        "What database does this project use?",
        max_iterations=1,
    )

    assert result == "The database uses SQLite."

    assert len(captured_calls) == 1

    prompt = captured_calls[0]["input"]

    assert "REPOSITORY CONTEXT:" in prompt
    assert "app/database.py" in prompt
    assert "DATABASE_URL" in prompt
    assert "What database does this project use?" in prompt

def test_run_falls_back_to_ollama_when_gemini_fails(
    monkeypatch,
):
    class FakeGemini:
        def create_interaction(self, prompt, tools):
            raise RuntimeError("Gemini quota exceeded")

    class FakeOllama:
        def generate(self, prompt):
            assert "Test task" in prompt
            return "Ollama fallback response"

    agent = SoftwareEngineeringAgent()

    agent.llm = FakeGemini()
    agent.fallback_llm = FakeOllama()

    result = agent.run(
        "Test task",
        max_iterations=1,
    )

    assert result == "Ollama fallback response"