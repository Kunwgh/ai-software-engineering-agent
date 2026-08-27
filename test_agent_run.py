from app.agents.agent import SoftwareEngineeringAgent


def main():
    agent = SoftwareEngineeringAgent()

    result = agent.run(
        "Inspect test_tools.py first. "
        "Then add a comment '# Tested by SoftwareEngineeringAgent' "
        "to the top of the file. "
        "After editing it, read the file again to verify the change. "
        "Finally run 'python test_tools.py' and report whether the test passed.",
        max_iterations=10,
    )

    print("\n=== FINAL AGENT RESPONSE ===")
    print(result)


if __name__ == "__main__":
    main()