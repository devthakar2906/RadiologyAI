import asyncio
import json
import re
from functools import lru_cache

from huggingface_hub import InferenceClient

from app.core.config import get_settings


settings = get_settings()


@lru_cache
def get_llm_client() -> InferenceClient:
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not configured.")
    return InferenceClient(api_key=settings.hf_token)


def _extract_content(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()
    return str(content or "").strip()


def _sync_generate_report(prompt: str) -> str:
    client = get_llm_client()
    completion = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": "You are an expert radiologist. Return strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=700,
    )
    return _extract_content(completion.choices[0].message.content)


async def generate_report(prompt: str) -> str:
    last_error: Exception | None = None
    for attempt in range(settings.hf_max_retries):
        try:
            return await asyncio.to_thread(_sync_generate_report, prompt)
        except Exception as exc:
            last_error = exc
            if attempt == settings.hf_max_retries - 1:
                break
            await asyncio.sleep(min(2 ** attempt, 8))
    raise RuntimeError(f"LLM report generation failed: {last_error}") from last_error


def parse_llm_json(raw_text: str) -> dict:
    candidate = raw_text.strip()
    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", candidate, flags=re.DOTALL | re.IGNORECASE)
    if fenced_match:
        candidate = fenced_match.group(1).strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(candidate[start : end + 1])
        raise
