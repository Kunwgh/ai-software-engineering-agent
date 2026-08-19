TOOL_SCHEMAS = {
    "scan_repository": {
        "description": "Scan a repository and return a list of source files.",
        "arguments": {
            "repository_path": {
                "type": "string",
                "description": "Path to the repository.",
            }
        },
    },
    "read_file": {
        "description": "Read the contents of a file inside a repository.",
        "arguments": {
            "repository_path": {
                "type": "string",
                "description": "Path to the repository.",
            },
            "file_path": {
                "type": "string",
                "description": "Path of the file relative to the repository.",
            },
        },
    },
}