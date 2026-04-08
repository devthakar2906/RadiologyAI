def format_report(report_json: dict) -> str:
    lines: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                lines.append(f"{key}:")
                walk(value)
        else:
            text = str(node or "Not mentioned").strip() or "Not mentioned"
            lines.append(text)
            lines.append("")

    walk(report_json)
    return "\n".join(lines).strip()
