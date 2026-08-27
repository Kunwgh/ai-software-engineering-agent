from app.tools.registry import TOOLS
from app.tools.schemas import TOOL_SCHEMAS


class ToolExecutor:
    def execute(self, tool_name: str, arguments: dict):
        # Check that the requested tool exists.
        if tool_name not in TOOLS:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        # Get the actual Python function.
        tool = TOOLS[tool_name]

        # Get the schema for this tool.
        schema = TOOL_SCHEMAS[tool_name]

        # Make a copy so we don't modify Gemini's
        # original arguments.
        arguments = dict(arguments)

        # Normalize common LLM argument variations.
        if tool_name == "read_file":
            if "path" in arguments and "file_path" not in arguments:
                arguments["file_path"] = arguments.pop("path")

            if "repository_path" not in arguments:
                arguments["repository_path"] = "."

        if tool_name == "write_file":
            if "path" in arguments and "file_path" not in arguments:
                arguments["file_path"] = arguments.pop("path")

            if "repository_path" not in arguments:
                arguments["repository_path"] = "."

            # Validate all required arguments.
        for argument_name in schema.get("required", []):
            if argument_name not in arguments:
                raise ValueError(
                    f"Missing required argument "
                    f"'{argument_name}' for tool '{tool_name}'"
                )

        # Reject arguments that are not defined by the tool schema.
        allowed_arguments = set(
            schema.get("arguments", {}).keys()
        )

        for argument_name in arguments:
            if argument_name not in allowed_arguments:
                raise ValueError(
                    f"Unexpected argument "
                    f"'{argument_name}' for tool '{tool_name}'"
                )

        # Execute the validated tool and return its result.
        return tool(**arguments)