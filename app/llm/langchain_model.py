import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from app.tools.langchain_tools import LANGCHAIN_TOOLS


load_dotenv()


class LangChainGemini:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set in the .env file"
            )

        self.model = init_chat_model(
            "google_genai:gemini-3.6-flash",
            google_api_key=api_key,
        )

        self.tool_model = self.model.bind_tools(
            LANGCHAIN_TOOLS
        )

    def generate(self, prompt: str) -> str:
        response = self.model.invoke(prompt)

        if isinstance(response.content, str):
            return response.content

        return "".join(
            block.get("text", "")
            for block in response.content
            if block.get("type") == "text"
        )

    def invoke_with_tools(self, prompt: str):
        return self.tool_model.invoke(prompt)

    def run_tool_cycle(self, prompt: str):
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        response = self.tool_model.invoke(messages)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            arguments = tool_call["args"]

            print(f"\nTool requested: {tool_name}")
            print(f"Arguments: {arguments}")

            # Map LangChain wrapper names to existing application tools.
            existing_tool_name = tool_name.removeprefix("lc_")

            from app.tools.executor import ToolExecutor

            executor = ToolExecutor()

            result = executor.execute(
                existing_tool_name,
                arguments,
            )

            print(f"\nTool result:\n{result}")

            messages.append(response)
            messages.append(
                {
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call["id"],
                }
            )

        final_response = self.tool_model.invoke(messages)

        return final_response.content