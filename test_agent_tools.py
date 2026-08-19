from app.agents.agent import SoftwareEngineeringAgent


agent = SoftwareEngineeringAgent()

result = agent.use_tool(
    "read_file",
    {
        "repository_path": ".",
        "file_path": "app/agents/agent.py",
    },
)

print(result)