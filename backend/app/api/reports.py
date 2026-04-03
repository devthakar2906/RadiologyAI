from pathlib import Path
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Report, User
from app.schemas.report import (
    JobStatusResponse,
    ProcessAudioResponse,
    ReportPayload,
    ReportResponse,
    TranscriptionResponse,
)
from app.services.logging_service import create_log
from app.services.redis_client import get_cached_report
from app.services.report_pipeline import process_audio_pipeline, process_transcription_pipeline
from app.services.security import decrypt_text, generate_audio_hash
from app.services.ai import transcribe_audio
from app.workers.celery_app import celery_app
from app.workers.tasks import process_audio_task


settings = get_settings()
router = APIRouter(tags=["reports"])


def _serialize_report(report: Report) -> ReportResponse:
    return ReportResponse(
        id=report.id,
        user_id=report.user_id,
        transcription=decrypt_text(report.transcription),
        report=ReportPayload.model_validate_json(decrypt_text(report.report)),
        audio_hash=report.audio_hash,
        created_at=report.created_at,
    )


def _has_active_worker() -> bool:
    try:
        inspector = celery_app.control.inspect(timeout=1.0)
        active_workers = inspector.ping() or {}
        return bool(active_workers)
    except Exception:
        return False


@router.post("/process-audio", response_model=ProcessAudioResponse)
async def process_audio(
    file: UploadFile | None = File(default=None),
    transcription_text: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    cleaned_text = (transcription_text or "").strip()

    if file is None and not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either an audio file or transcription_text.",
        )

    if file is None and cleaned_text:
        text_hash = generate_audio_hash(cleaned_text.encode("utf-8"))
        cached = get_cached_report(text_hash)
        if cached:
            return ProcessAudioResponse(status="completed", cached=True, data=ReportResponse(**cached))

        try:
            payload = process_transcription_pipeline(
                db,
                transcription=cleaned_text,
                user_id=str(current_user.id),
                audio_path="manual-text",
                audio_hash=text_hash,
            )
            return ProcessAudioResponse(status="completed", cached=False, data=ReportResponse(**payload))
        except Exception as exc:
            create_log(db, current_user.id, "process_text_report", f"failed:{exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Text report generation failed: {exc}",
            ) from exc

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty audio file")

    audio_hash = generate_audio_hash(content)
    cached = get_cached_report(audio_hash)
    if cached:
        return ProcessAudioResponse(status="completed", cached=True, data=ReportResponse(**cached))

    destination = Path(settings.uploads_dir) / f"{audio_hash}_{file.filename}"
    destination.write_bytes(content)

    if not _has_active_worker():
        try:
            payload = process_audio_pipeline(
                db,
                audio_path=str(destination),
                audio_hash=audio_hash,
                user_id=str(current_user.id),
            )
            return ProcessAudioResponse(status="completed", cached=False, data=ReportResponse(**payload))
        except Exception as exc:
            create_log(db, current_user.id, "process_audio", f"failed:{exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Audio processing failed: {exc}",
            ) from exc

    task = process_audio_task.delay(audio_path=str(destination), audio_hash=audio_hash, user_id=str(current_user.id))
    return ProcessAudioResponse(job_id=task.id, status="queued", cached=False)


@router.post("/transcribe-audio", response_model=TranscriptionResponse)
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty audio file")

    audio_hash = generate_audio_hash(content)
    destination = Path(settings.uploads_dir) / f"refine_{audio_hash}_{file.filename}"
    destination.write_bytes(content)

    try:
        transcription = transcribe_audio(str(destination))
        return TranscriptionResponse(transcription=transcription)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio transcription failed: {exc}",
        ) from exc
    finally:
        if destination.exists():
            destination.unlink(missing_ok=True)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, current_user: User = Depends(require_role("doctor", "admin"))):
    result = AsyncResult(job_id, app=process_audio_task.app)
    if result.successful():
        return JobStatusResponse(job_id=job_id, status="completed", result=ReportResponse(**result.result))
    if result.failed():
        return JobStatusResponse(job_id=job_id, status="failed", error=str(result.result))
    return JobStatusResponse(job_id=job_id, status=result.status.lower())


@router.get("/reports", response_model=list[ReportResponse])
def list_reports(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    query = select(Report)
    if current_user.role != "admin":
        query = query.where(Report.user_id == current_user.id)
    if search:
        query = query.where(Report.audio_hash.ilike(f"%{search}%"))
    reports = db.scalars(query.order_by(Report.created_at.desc())).all()
    return [_serialize_report(report) for report in reports]


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    if current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    audio_path = Path(report.audio_path)
    db.execute(delete(Report).where(Report.id == report_id))
    db.commit()
    if audio_path.exists():
        audio_path.unlink(missing_ok=True)
    create_log(db, current_user.id, "delete_report", "success")
