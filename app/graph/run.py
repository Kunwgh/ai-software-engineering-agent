from langchain_core.messages import HumanMessage

from app.graph.graph import graph


task = "List the files in the current repository."

result = graph.invoke(
    {
        "task": task,
        "messages": [
            HumanMessage(content=task)
        ],
    }
)

for message in result["messages"]:
    print("\n--- MESSAGE ---")
    print("Type:", type(message).__name__)
    print("Content:", message.content)

    if getattr(message, "tool_calls", None):
        print("Tool calls:", message.tool_calls)