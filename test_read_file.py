from app.tools.repository import read_file


content = read_file(".", "app/agents/agent.py")

print(content)