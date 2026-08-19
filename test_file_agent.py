from app.agents.agent import SoftwareEngineeringAgent


agent = SoftwareEngineeringAgent()

analysis = agent.inspect_file(
    ".",
    "app/agents/agent.py",
)

print(analysis)