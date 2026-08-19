from app.tools.executor import ToolExecutor


executor = ToolExecutor()

result = executor.execute(
    "read_file",
    {
        "repository_path": ".",
        "file_path": "app/agents/agent.py",
    },
)

print(result)