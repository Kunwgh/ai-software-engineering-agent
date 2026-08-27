import json

from app.database.repository import (
    create_task,
    create_agent_run,
    create_tool_call,
    update_task_status,
    update_agent_run_status,
)

from app.llm.gemini_client import GeminiClient
from app.tools.repository import scan_repository, read_file
from app.tools.executor import ToolExecutor
from app.tools.schemas import TOOL_SCHEMAS


class SoftwareEngineeringAgent:
    def __init__(self):
        self.llm = GeminiClient()
        self.tool_executor = ToolExecutor()

    def _get_gemini_tools(self):
        tools = []

        for tool_name, schema in TOOL_SCHEMAS.items():
            tools.append(
                {
                    "type": "function",
                    "name": tool_name,
                    "description": schema["description"],
                    "parameters": {
                        "type": "object",
                        "properties": schema["arguments"],
                        "required": schema["required"],

                    },
                }
            )

        return tools

    def run(self, task: str, max_iterations: int = 10) -> str:
        if max_iterations <= 0:
            raise ValueError("max_iterations must be greater than 0")

        task_id = create_task(task)

        iteration = 1

        run_id = create_agent_run(
        task_id,
        iteration,
        )

        response = self.llm.create_interaction(
            task,
            self._get_gemini_tools(),
        )

        while True:
            if iteration >= max_iterations:
                raise RuntimeError(
                    f"Agent exceeded maximum iterations: {max_iterations}"
                )

            iteration += 1

            function_calls = [
                step
                for step in response.steps
                if step.type == "function_call"
            ]

            if not function_calls:
                update_agent_run_status(run_id, "completed")
                update_task_status(task_id, "completed")
                
                return response.output_text

            function_results = []

            for call in function_calls:
                try:
                    tool_result = self.tool_executor.execute(
                    call.name,
                    call.arguments,
                    )   

                    # Gemini expects the function result to be
                    # JSON-compatible. Convert Python values to JSON text.
                    if isinstance(tool_result, str):
                        result = tool_result
                    else:
                        result = json.dumps(tool_result, indent=2)

                except Exception as e:
                    # Do not crash the agent when a tool call fails.
                    # Send the error back to Gemini so it can correct its call.
                    result = f"Tool execution failed: {str(e)}"

                create_tool_call(
                    run_id,
                    call.name,
                    json.dumps(call.arguments),
                    result,
                )

                function_results.append(
                    {
                        "type": "function_result",
                        "call_id": call.id,
                        "name": call.name,
                        "result": result,
                    }
                )

            response = self.llm.continue_interaction(
                response.id,
                function_results,
            )

    def ask(self, task: str) -> str:
        return self.llm.generate(task)

    def inspect_repository(self, repository_path: str) -> str:
        files = scan_repository(repository_path)

        file_list = "\n".join(files)

        prompt = f"""
You are a software engineering agent.

Here is the file structure of a software repository:

{file_list}

Analyze this repository structure and provide:
1. A brief description of what kind of project it appears to be.
2. The important files or directories you would inspect first.
3. Any obvious observations about the project structure.

Do not assume the contents of files that you have not seen.
"""

        return self.llm.generate(prompt)

    def inspect_file(
        self,
        repository_path: str,
        file_path: str,
    ) -> str:
        content = read_file(repository_path, file_path)

        prompt = f"""
You are a software engineering agent.

Analyze the following source code.

File: {file_path}

SOURCE CODE:
{content}

Provide:
1. What this file does.
2. The important classes, functions, or components.
3. Any obvious problems or risks.
4. How this file relates to the rest of the project based only on the code provided.

Do not invent information that is not present in the code.
"""

        return self.llm.generate(prompt)

    def use_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        return self.tool_executor.execute(
            tool_name,
            arguments,
        )