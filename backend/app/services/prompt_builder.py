import json


def build_prompt(template: dict, findings: str) -> str:
    template_json = json.dumps(template, ensure_ascii=False, indent=2)
    return (
        "You are an expert radiologist.\n\n"
        "Follow the given structured template STRICTLY.\n\n"
        f"TEMPLATE:\n{template_json}\n\n"
        f"FINDINGS:\n{findings}\n\n"
        "INSTRUCTIONS:\n"
        '- Add a top-level "_meta" object with a "template_name" field.\n'
        '- The "template_name" must be a short, professional radiology template/report name that best matches the findings.\n'
        "- Fill all fields\n"
        "- If missing, write 'Not mentioned'\n"
        "- Keep language clinically concise\n"
        "- Return ONLY valid JSON"
    )
