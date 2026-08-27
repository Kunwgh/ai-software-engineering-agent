from app.agents.agent import SoftwareEngineeringAgent


def main():
    agent = SoftwareEngineeringAgent()

    result = agent.run(
        "Make test_tools.py fail, run it, fix it, and run it again.",
        max_iterations=6,
    )

    print("\n=== FINAL AGENT RESPONSE ===")
    print(result)


if __name__ == "__main__":
    main()