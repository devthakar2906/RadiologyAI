import hashlib
import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Report
from app.services.ai import clean_transcription_text, transcribe_audio_async
from app.services.logging_service import create_log
from app.services.redis_client import set_cached_report
from app.services.security import encrypt_text
from app.services.structured_report_service import generate_structured_report


async def process_audio_pipeline(db: Session, *, audio_path: str, audio_hash: str, user_id: str) -> dict:
    transcription = await transcribe_audio_async(audio_path)
    return await process_transcription_pipeline(
        db,
        transcription=transcription,
        audio_hash=audio_hash,
        user_id=user_id,
        audio_path=audio_path,
    )


async def process_transcription_pipeline(
    db: Session,
    *,
    transcription: str,
    user_id: str,
    audio_path: str = "manual-text",
    audio_hash: str | None = None,
) -> dict:
    cleaned_transcription = clean_transcription_text(transcription)
    resolved_hash = audio_hash or hashlib.sha256(cleaned_transcription.encode("utf-8")).hexdigest()
    structured = await generate_structured_report(cleaned_transcription)
    report_sections = structured["structured_json"]
    report_template = structured.get("template")
    formatted_report = structured.get("formatted_report")
    study_type = structured.get("study_type")

    report = Report(
        user_id=UUID(user_id),
        transcription=encrypt_text(cleaned_transcription),
        report=encrypt_text(json.dumps(report_sections)),
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
        "report": report_sections,
        "template": report_template,
        "formatted_report": formatted_report,
        "study_type": study_type,
        "audio_hash": resolved_hash,
        "created_at": report.created_at.isoformat(),
    }
    set_cached_report(resolved_hash, payload)
    create_log(db, UUID(user_id), "process_audio", "completed")
    return payload
