from datetime import datetime

from google import genai
from dotenv import load_dotenv

from app.tools.executor import ToolExecutor
from app.tools.registry import TOOLS


load_dotenv()


def get_time():
    """Return the current local time."""
    return datetime.now().strftime("%H:%M:%S")


# Temporarily register the fake tool for this test.
TOOLS["get_time"] = get_time


api_key = __import__("os").getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

executor = ToolExecutor()


response = client.interactions.create(
    model="gemini-3.6-flash",
    input="What time is it? Use the get_time tool.",
    tools=[
        {
            "type": "function",
            "name": "get_time",
            "description": "Get the current time.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }
    ],
)


print("Gemini status:", response.status)


for step in response.steps:

    if step.type == "function_call":

        print("Gemini requested tool:", step.name)
        print("Arguments:", step.arguments)

        tool_result = executor.execute(
            step.name,
            step.arguments,
        )

        print("Tool result:", tool_result)

function_result = {
            "type": "function_result",
            "call_id": step.id,
            "name": step.name,
            "result": tool_result,
        }

final_response = client.interactions.create(
            model="gemini-3.6-flash",
            previous_interaction_id=response.id,
            input=[function_result],
        )

print("Final Gemini response:", final_response.output_text)