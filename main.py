from app.agents.agent import SoftwareEngineeringAgent


def main():
    agent = SoftwareEngineeringAgent()

    print("AI Software Engineering Agent")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            response = agent.run(user_input)
            print("Assistant:", response)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()