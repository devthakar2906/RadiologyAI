import html
import mimetypes
import re
from pathlib import Path

import httpx

from app.core.config import get_settings


settings = get_settings()


def clean_transcription_text(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _get_headers(content_type: str = "application/json") -> dict[str, str]:
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not configured.")
    return {
        "Authorization": f"Bearer {settings.hf_token}",
        "Content-Type": content_type,
    }


def _parse_generated_text(payload) -> str:
    if isinstance(payload, dict):
        if isinstance(payload.get("text"), str):
            return payload["text"]
        if isinstance(payload.get("generated_text"), str):
            return payload["generated_text"]
        if "error" in payload:
            raise RuntimeError(str(payload["error"]))

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    return item["text"]
                if isinstance(item.get("generated_text"), str):
                    return item["generated_text"]

    if isinstance(payload, str):
        return payload

    raise RuntimeError("Unexpected response from Hugging Face API.")


def transcribe_audio(audio_path: str) -> str:
    audio_file = Path(audio_path)
    mime_type = mimetypes.guess_type(audio_file.name)[0] or "application/octet-stream"

    with audio_file.open("rb") as source:
        response = httpx.post(
            f"https://api-inference.huggingface.co/models/{settings.stt_model}",
            headers=_get_headers(mime_type),
            params={"wait_for_model": "true"},
            content=source.read(),
            timeout=120.0,
        )
    response.raise_for_status()
    return clean_transcription_text(_parse_generated_text(response.json()))


def refine_with_medasr(text: str) -> str:
    cleaned = clean_transcription_text(text)
    if not cleaned:
        return ""

    prompt = (
        "You are a medical ASR expert.\n\n"
        "Correct this radiology dictation. Preserve clinical meaning, measurements, and anatomy. "
        "Return only the corrected dictation text.\n\n"
        f"{cleaned}"
    )

    try:
        response = httpx.post(
            f"https://api-inference.huggingface.co/models/{settings.stt_model}",
            headers=_get_headers(),
            params={"wait_for_model": "true"},
            json={"inputs": prompt},
            timeout=120.0,
        )
        response.raise_for_status()
        refined = clean_transcription_text(_parse_generated_text(response.json()))
        return refined or cleaned
    except Exception:
        return cleaned
