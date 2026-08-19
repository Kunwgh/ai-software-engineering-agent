from app.agents.agent import SoftwareEngineeringAgent


agent = SoftwareEngineeringAgent()

analysis = agent.inspect_repository(".")

print(analysis)