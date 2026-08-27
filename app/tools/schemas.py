TOOL_SCHEMAS = {
    "scan_repository": {
        "description": "Scan a repository and return a list of source files.",
        "arguments": {
            "repository_path": {
                "type": "string",
                "description": "Path to the repository.",
            }
        },
        "required": [
            "repository_path",
        ],
    },
    "read_file": {
        "description": (
            "Read the contents of a file inside a repository. "
            "You MUST provide both repository_path and file_path. "
            "repository_path is the repository root directory, such as '.'. "
            "file_path is the file path relative to that repository root, "
            "such as 'app/agents/agent.py'. "
            "Do not use 'path'. Use the exact argument name 'file_path'."
),
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
        "required": [
            "repository_path",
            "file_path",
        ],
    },
    "write_file": {
        "description": (
            "Write or overwrite a file inside a repository. "
            "You MUST provide repository_path, file_path, and content. "
            "repository_path is the repository root directory, such as '.'. "
            "file_path is the file path relative to that repository root, "
            "such as 'app/example.py'. "
            "content is the complete text that should be written to the file."
        ),
        "arguments": {
            "repository_path": {
                "type": "string",
                "description": "Path to the repository.",
            },
            "file_path": {
                "type": "string",
                "description": "Path of the file relative to the repository.",
            },
            "content": {
                "type": "string",
                "description": "Complete content to write to the file.",
            },
        },
        "required": [
            "repository_path",
            "file_path",
            "content",
        ],
    },
    "edit_file": {
        "description": (
        "Edit a file inside a repository by replacing one exact piece "
        "of text with new text. You MUST provide repository_path, "
        "file_path, old_text, and new_text. "
        "old_text must exactly match text that already exists in the file."
        ),
        "arguments": {
            "repository_path": {
            "type": "string",
            "description": "Path to the repository.",
            },
            "file_path": {
            "type": "string",
            "description": "Path of the file relative to the repository.",
            },
            "old_text": {
            "type": "string",
            "description": "Exact text currently present in the file.",
            },
            "new_text": {
            "type": "string",
            "description": "New text that should replace old_text.",
            },
        },
        "required": [
        "repository_path",
        "file_path",
        "old_text",
        "new_text",
        ],
    },
    "run_command": {
        "description": (
        "Run a shell command inside the repository. "
        "You MUST provide repository_path and command. "
        "Use this tool to run tests, inspect command output, "
        "or perform other software engineering tasks."
        ),
        "arguments": {
        "repository_path": {
            "type": "string",
            "description": "Path to the repository.",
        },
        "command": {
            "type": "string",
            "description": "Shell command to execute.",
        },
        },
        "required": [
        "repository_path",
        "command",
        ],
    },
}