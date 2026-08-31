import pytest

from mcp import Client

from app.mcp_server import mcp


@pytest.mark.anyio
async def test_mcp_server_lists_tools():
    async with Client(mcp) as client:
        result = await client.list_tools()

    tool_names = {tool.name for tool in result.tools}

    assert "scan_repository_tool" in tool_names
    assert "read_file_tool" in tool_names

@pytest.mark.anyio
async def test_mcp_can_call_read_file_tool(tmp_path):
    test_file = tmp_path / "example.txt"
    test_file.write_text(
        "hello from MCP",
        encoding="utf-8",
    )

    async with Client(mcp) as client:
        result = await client.call_tool(
            "read_file_tool",
            {
                "repository_path": str(tmp_path),
                "file_path": "example.txt",
            },
        )

    assert result.content[0].text == "hello from MCP"