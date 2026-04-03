import html
import json
import os
import re
from functools import lru_cache

import librosa
from transformers import pipeline

from app.core.config import get_settings


settings = get_settings()

if settings.hf_token:
    os.environ["HF_TOKEN"] = settings.hf_token


@lru_cache
def get_asr_pipeline():
    return pipeline(
        "automatic-speech-recognition",
        model=settings.stt_model,
        token=settings.hf_token,
        trust_remote_code=True,
    )


@lru_cache
def get_summarizer():
    return pipeline("summarization", model=settings.summarization_model, token=settings.hf_token)


def transcribe_audio(audio_path: str) -> str:
    asr = get_asr_pipeline()
    # MedASR expects mono 16kHz audio. librosa normalizes the input to that shape/rate.
    speech, sample_rate = librosa.load(audio_path, sr=16000, mono=True)
    result = asr({"array": speech, "sampling_rate": sample_rate}, chunk_length_s=20, stride_length_s=2)
    if isinstance(result, dict):
        return clean_transcription_text(result.get("text", ""))
    return clean_transcription_text(str(result))


def clean_transcription_text(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def summarize_transcription(transcription: str) -> dict:
    cleaned = clean_transcription_text(transcription)
    prompt = (
        "Summarize this radiology transcription into findings, impression, and recommendations. "
        "Keep the language clinical and concise. "
        f"Transcription: {cleaned}"
    )
    summarizer = get_summarizer()
    input_words = max(len(cleaned.split()), 1)
    max_new_tokens = min(96, max(24, input_words // 2))
    min_new_tokens = min(24, max(8, input_words // 5))
    summary = summarizer(
        prompt,
        max_new_tokens=max_new_tokens,
        min_new_tokens=min_new_tokens,
        do_sample=False,
    )[0]["summary_text"]
    try:
        parsed = json.loads(summary)
    except json.JSONDecodeError:
        parsed = {
            "findings": cleaned[:400] or "No findings available.",
            "impression": _derive_impression(cleaned, summary),
            "recommendations": "Clinical correlation recommended.",
        }

    return {
        "findings": clean_transcription_text(parsed.get("findings", "")) or "No findings available.",
        "impression": clean_transcription_text(parsed.get("impression", "")) or _derive_impression(cleaned, summary),
        "recommendations": parsed.get("recommendations", "Clinical correlation recommended."),
    }


def _derive_impression(transcription: str, summary: str) -> str:
    cleaned_summary = clean_transcription_text(summary)
    if "json keys" in cleaned_summary.lower() or cleaned_summary.lower().startswith("a radiology report"):
        cleaned_summary = ""
    if cleaned_summary:
        return cleaned_summary[:250]
    sentence = transcription.split(".")[0].strip()
    return sentence[:250] if sentence else "No impression available."
