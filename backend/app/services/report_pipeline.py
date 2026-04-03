import hashlib
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Report
from app.schemas.report import ReportPayload
from app.services.ai import clean_transcription_text, summarize_transcription, transcribe_audio
from app.services.logging_service import create_log
from app.services.redis_client import set_cached_report
from app.services.security import encrypt_text


def process_audio_pipeline(db: Session, *, audio_path: str, audio_hash: str, user_id: str) -> dict:
    transcription = transcribe_audio(audio_path)
    return process_transcription_pipeline(
        db,
        transcription=transcription,
        audio_hash=audio_hash,
        user_id=user_id,
        audio_path=audio_path,
    )


def process_transcription_pipeline(
    db: Session,
    *,
    transcription: str,
    user_id: str,
    audio_path: str = "manual-text",
    audio_hash: str | None = None,
) -> dict:
    cleaned_transcription = clean_transcription_text(transcription)
    resolved_hash = audio_hash or hashlib.sha256(cleaned_transcription.encode("utf-8")).hexdigest()
    report_data = summarize_transcription(cleaned_transcription)

    report = Report(
        user_id=UUID(user_id),
        transcription=encrypt_text(cleaned_transcription),
        report=encrypt_text(ReportPayload(**report_data).model_dump_json()),
        audio_hash=resolved_hash,
        audio_path=audio_path,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    payload = {
        "id": str(report.id),
        "user_id": user_id,
        "transcription": cleaned_transcription,
        "report": report_data,
        "audio_hash": resolved_hash,
        "created_at": report.created_at.isoformat(),
    }
    set_cached_report(resolved_hash, payload)
    create_log(db, UUID(user_id), "process_audio", "completed")
    return payload
