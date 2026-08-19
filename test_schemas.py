from app.tools.schemas import TOOL_SCHEMAS


for tool_name, schema in TOOL_SCHEMAS.items():
    print(f"\nTool: {tool_name}")
    print(f"Description: {schema['description']}")
    print("Arguments:")

    for argument_name, argument in schema["arguments"].items():
        print(
            f"  - {argument_name}: "
            f"{argument['type']} - "
            f"{argument['description']}"
        )