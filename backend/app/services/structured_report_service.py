import hashlib

from app.services.ai import clean_transcription_text
from app.services.formatter import format_report
from app.services.llm_service import generate_report, parse_llm_json
from app.services.prompt_builder import build_prompt
from app.services.study_detector import detect_study_type
from app.services.template_service import get_template


def _first_meaningful_sentence(text: str) -> str:
    sentences = [part.strip() for part in text.replace("\n", " ").split(".") if part.strip()]
    return sentences[0] if sentences else text.strip()


def _all_not_mentioned(node) -> bool:
    if isinstance(node, dict):
        return all(_all_not_mentioned(value) for value in node.values())
    return str(node or "").strip().lower() in {"", "not mentioned"}


def _heuristic_fill(template, findings: str):
    summary = findings.strip() or "Not mentioned"
    impression = _first_meaningful_sentence(summary) or "Not mentioned"

    if isinstance(template, dict):
        result = {}
        for key, value in template.items():
            normalized = key.lower()
            if normalized == "impression":
                result[key] = impression
            elif normalized == "recommendations":
                result[key] = "Clinical correlation recommended." if summary != "Not mentioned" else "Not mentioned"
            elif normalized == "technique":
                result[key] = "Not mentioned"
            elif normalized == "findings":
                result[key] = _heuristic_fill(value, findings)
            else:
                result[key] = _heuristic_fill(value, findings)
        return result

    return summary if summary else "Not mentioned"


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
        try:
            return parse_llm_json(retry_raw)
        except Exception:
            return {}


async def generate_structured_report(findings: str) -> dict:
    cleaned = clean_transcription_text(findings)
    study_type = detect_study_type(cleaned)
    template, template_source = await get_template(study_type, cleaned)
    prompt = build_prompt(template, cleaned)
    generated_json = await _generate_with_retry(prompt)
    structured = _fill_missing(template, generated_json)

    # If the model returns empty or unusable content, fall back to a deterministic
    # structure derived directly from the findings so the UI always has content.
    if _all_not_mentioned(structured):
        structured = _heuristic_fill(template, cleaned)

    structured["Transcription"] = cleaned or "Not mentioned"

    return {
        "study_type": study_type,
        "template": template_source,
        "structured_json": structured,
        "formatted_report": format_report(structured),
        "input_hash": hashlib.sha256(cleaned.encode("utf-8")).hexdigest(),
    }
