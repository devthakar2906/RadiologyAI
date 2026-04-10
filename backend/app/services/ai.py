import asyncio
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


async def _request_with_retry(*, content=None, json_body=None, content_type: str) -> str:
    last_error: Exception | None = None

    for attempt in range(settings.hf_max_retries):
        try:
            async with httpx.AsyncClient(timeout=settings.hf_request_timeout_seconds) as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{settings.stt_model}",
                    headers=_get_headers(content_type),
                    params={"wait_for_model": "true"},
                    content=content,
                    json=json_body,
                )
                response.raise_for_status()
                return clean_transcription_text(_parse_generated_text(response.json()))
        except Exception as exc:
            last_error = exc
            if attempt == settings.hf_max_retries - 1:
                break
            await asyncio.sleep(min(2 ** attempt, 8))

    raise RuntimeError(f"Hugging Face request failed: {last_error}") from last_error


async def transcribe_audio_async(audio_path: str) -> str:
    audio_file = Path(audio_path)
    mime_type = mimetypes.guess_type(audio_file.name)[0] or "application/octet-stream"
    return await _request_with_retry(content=audio_file.read_bytes(), content_type=mime_type)


def transcribe_audio(audio_path: str) -> str:
    return asyncio.run(transcribe_audio_async(audio_path))


async def refine_with_medasr_async(text: str) -> str:
    # MedASR is an ASR model, so text-only "refinement" should stay lightweight
    # and deterministic instead of sending unsupported prompt-generation calls.
    return clean_transcription_text(text)


def refine_with_medasr(text: str) -> str:
    return asyncio.run(refine_with_medasr_async(text))
