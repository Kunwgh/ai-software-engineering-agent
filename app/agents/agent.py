from app.llm.gemini_client import GeminiClient
from app.tools.repository import scan_repository, read_file
from app.tools.executor import ToolExecutor



class SoftwareEngineeringAgent:
    def __init__(self):
        self.llm = GeminiClient()
        self.tool_executor = ToolExecutor()


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
    