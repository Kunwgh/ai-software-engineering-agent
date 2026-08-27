from app.tools.schemas import TOOL_SCHEMAS


def test_all_tools_have_schemas():
    expected_tools = {
        "scan_repository",
        "read_file",
        "write_file",
        "edit_file",
        "run_command",
    }

    assert set(TOOL_SCHEMAS.keys()) == expected_tools


def test_required_arguments_exist():
    for tool_name, schema in TOOL_SCHEMAS.items():
        assert "description" in schema
        assert "arguments" in schema
        assert "required" in schema

        for argument in schema["required"]:
            assert argument in schema["arguments"]