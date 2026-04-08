import hashlib

from app.services.ai import clean_transcription_text
from app.services.formatter import format_report
from app.services.llm_service import generate_report, parse_llm_json
from app.services.prompt_builder import build_prompt
from app.services.study_detector import detect_study_type
from app.services.template_service import get_template


def _fill_missing(template, generated):
    if isinstance(template, dict):
        result = {}
        generated = generated if isinstance(generated, dict) else {}
        for key, value in template.items():
            result[key] = _fill_missing(value, generated.get(key))
        for key, value in generated.items():
            if key not in result:
                result[key] = _fill_missing("Not mentioned", value)
        return result

    if isinstance(generated, dict):
        return {key: _fill_missing("Not mentioned", value) for key, value in generated.items()}

    value = str(generated or "").strip()
    return value or "Not mentioned"


async def _generate_with_retry(prompt: str) -> dict:
    raw = await generate_report(prompt)
    try:
        return parse_llm_json(raw)
    except Exception:
        retry_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT RETRY:\n"
            "- Your previous answer was not valid JSON.\n"
            "- Return one JSON object only.\n"
            "- No markdown, no explanation, no code fences.\n"
        )
        retry_raw = await generate_report(retry_prompt)
        return parse_llm_json(retry_raw)


async def generate_structured_report(findings: str) -> dict:
    cleaned = clean_transcription_text(findings)
    study_type = detect_study_type(cleaned)
    template, template_source = await get_template(study_type, cleaned)
    prompt = build_prompt(template, cleaned)
    generated_json = await _generate_with_retry(prompt)
    structured = _fill_missing(template, generated_json)
    structured["Transcription"] = cleaned or "Not mentioned"

    return {
        "study_type": study_type,
        "template": template_source,
        "structured_json": structured,
        "formatted_report": format_report(structured),
        "input_hash": hashlib.sha256(cleaned.encode("utf-8")).hexdigest(),
    }
