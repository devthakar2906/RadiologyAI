import asyncio
import html
import re
import shutil
import subprocess
import wave
from array import array
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCTC, AutoProcessor

from app.core.config import get_settings


settings = get_settings()


def clean_transcription_text(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _transcode_audio_to_wav(audio_file: Path) -> Path:
    ffmpeg_path = getattr(settings, "ffmpeg_path", None) or shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("FFMPEG_PATH is not configured and ffmpeg is not available on PATH.")

    wav_path = audio_file.with_suffix(f"{audio_file.suffix}.medasr.wav")
    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-i",
            str(audio_file),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            str(wav_path),
        ],
        check=True,
        capture_output=True,
    )
    return wav_path


def _read_wav_as_float_samples(wav_path: Path) -> np.ndarray:
    with wave.open(str(wav_path), "rb") as wav_file:
        sample_width = wav_file.getsampwidth()
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())

    if sample_width != 2:
        raise RuntimeError(f"Unsupported sample width for MedASR input: {sample_width}")
    if channels != 1:
        raise RuntimeError(f"Expected mono audio for MedASR input, received {channels} channels")
    if sample_rate != 16000:
        raise RuntimeError(f"Expected 16kHz audio for MedASR input, received {sample_rate}Hz")

    pcm = array("h")
    pcm.frombytes(frames)
    return np.asarray(pcm, dtype=np.float32) / 32768.0


@lru_cache(maxsize=1)
def _get_processor():
    return AutoProcessor.from_pretrained(
        settings.stt_model,
        token=settings.hf_token,
        trust_remote_code=True,
        cache_dir=settings.stt_local_cache_dir,
    )


@lru_cache(maxsize=1)
def _get_model():
    model = AutoModelForCTC.from_pretrained(
        settings.stt_model,
        token=settings.hf_token,
        trust_remote_code=True,
        cache_dir=settings.stt_local_cache_dir,
    )
    model.eval()
    return model


def _transcribe_audio_local(audio_path: str) -> str:
    audio_file = Path(audio_path)
    wav_path = _transcode_audio_to_wav(audio_file)
    try:
        speech = _read_wav_as_float_samples(wav_path)
        processor = _get_processor()
        model = _get_model()

        inputs = processor(
            speech,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True,
        )
        with torch.no_grad():
            outputs = model(**inputs)
            predicted_ids = torch.argmax(outputs.logits, dim=-1)
        decoded = processor.batch_decode(predicted_ids)[0]
        return clean_transcription_text(decoded)
    finally:
        wav_path.unlink(missing_ok=True)


async def transcribe_audio_async(audio_path: str) -> str:
    return await asyncio.to_thread(_transcribe_audio_local, audio_path)


def transcribe_audio(audio_path: str) -> str:
    return asyncio.run(transcribe_audio_async(audio_path))


async def refine_with_medasr_async(text: str) -> str:
    return clean_transcription_text(text)


def refine_with_medasr(text: str) -> str:
    return asyncio.run(refine_with_medasr_async(text))
