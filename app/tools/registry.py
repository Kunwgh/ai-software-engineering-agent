from app.tools.repository import (
    scan_repository,
    read_file,
    write_file,
    edit_file,
    run_command,
)


TOOLS = {
    "scan_repository": scan_repository,
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "run_command": run_command,
}