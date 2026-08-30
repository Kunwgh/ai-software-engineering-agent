
def build_context(
    results: list[dict],
) -> str:
    if not results:
        return ""

    context_parts = []

    for result in results:
        context_parts.append(
            f"--- {result['file_path']} "
            f"(lines {result['start_line']}-"
            f"{result['end_line']}) ---\n"
            f"{result['content']}"
        )

    return "\n\n".join(context_parts)