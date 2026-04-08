import json
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
    DoctorFilterOption,
    GenerateStructuredReportRequest,
    GenerateStructuredReportResponse,
    JobStatusResponse,
    ProcessAudioResponse,
    ReportResponse,
    ReportUpdateRequest,
    TranscriptionResponse,
)
from app.services.logging_service import create_log
from app.services.redis_client import get_cached_report
from app.services.report_pipeline import process_audio_pipeline, process_transcription_pipeline
from app.services.security import decrypt_text, encrypt_text, generate_audio_hash
from app.services.ai import refine_with_medasr, transcribe_audio
from app.services.formatter import format_report
from app.services.structured_report_service import generate_structured_report
from app.workers.celery_app import celery_app
from app.workers.tasks import process_audio_task


settings = get_settings()
router = APIRouter(tags=["reports"])


def _serialize_report(report: Report) -> ReportResponse:
    report_sections = json.loads(decrypt_text(report.report))
    inferred_study_type = _infer_study_type_from_sections(report_sections)
    return ReportResponse(
        id=report.id,
        user_id=report.user_id,
        transcription=decrypt_text(report.transcription),
        report=report_sections,
        template=None,
        formatted_report=format_report(report_sections),
        study_type=inferred_study_type,
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
            payload = await process_transcription_pipeline(
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
            payload = await process_audio_pipeline(
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


@router.post("/generate-structured-report", response_model=GenerateStructuredReportResponse)
async def generate_structured_report_endpoint(
    payload: GenerateStructuredReportRequest,
    current_user: User = Depends(require_role("doctor", "admin")),
):
    result = await generate_structured_report(payload.findings)
    return GenerateStructuredReportResponse(
        structured_json=result["structured_json"],
        formatted_report=result["formatted_report"],
        study_type=result["study_type"],
    )


@router.post("/transcribe-audio", response_model=TranscriptionResponse)
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    raw_text: str | None = Form(default=None),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty audio file")

    audio_hash = generate_audio_hash(content)
    destination = Path(settings.uploads_dir) / f"refine_{audio_hash}_{file.filename}"
    destination.write_bytes(content)

    try:
        raw_transcription = (raw_text or "").strip() or transcribe_audio(str(destination))
        refined_transcription = refine_with_medasr(raw_transcription)
        return TranscriptionResponse(
            raw_text=raw_transcription,
            refined_text=refined_transcription,
            transcription=refined_transcription,
            status="success",
        )
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
    doctor_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    query = select(Report)
    if current_user.role != "admin":
        query = query.where(Report.user_id == current_user.id)
    elif doctor_id:
        query = query.where(Report.user_id == doctor_id)
    reports = db.scalars(query.order_by(Report.created_at.desc())).all()
    serialized = [_serialize_report(report) for report in reports]

    if search:
        tokens = [token.lower() for token in search.split() if token.strip()]

        def flatten_values(node):
            if isinstance(node, dict):
                values = []
                for value in node.values():
                    values.extend(flatten_values(value))
                return values
            return [str(node)]

        def matches(report: ReportResponse) -> bool:
            haystack = " ".join([report.transcription, *flatten_values(report.report)]).lower()
            return all(token in haystack for token in tokens)

        serialized = [report for report in serialized if matches(report)]

    return serialized


def _infer_study_type_from_sections(report_sections: dict[str, str]) -> str | None:
    keys = set(report_sections.keys())
    if {"Technique", "Findings", "Impression"}.issubset(keys):
        return "Structured Radiology"
    if {"Alignment & Curvature", "Vertebral Bodies", "Intervertebral Discs", "Spinal Canal & Nerves", "Facet Joints"}.issubset(keys):
        return "MRI Spine"
    return "General Radiology"


@router.get("/doctors", response_model=list[DoctorFilterOption])
def list_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    doctors = db.scalars(select(User).where(User.role == "doctor").order_by(User.name.asc())).all()
    return [DoctorFilterOption(id=doctor.id, name=doctor.name) for doctor in doctors]


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


@router.put("/reports/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: UUID,
    payload: ReportUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    report = db.get(Report, report_id)
    if report and current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    try:
        def sanitize_report(node):
            if isinstance(node, dict):
                return {str(key): sanitize_report(value) for key, value in node.items()}
            return str(node or "")

        cleaned_report = sanitize_report(payload.report)
        if not report:
            report = Report(
                user_id=current_user.id,
                transcription=encrypt_text(payload.transcription or ""),
                report=encrypt_text(json.dumps(cleaned_report)),
                audio_hash=generate_audio_hash((payload.transcription or "").encode("utf-8")),
                audio_path="manual-save",
            )
        else:
            report.transcription = encrypt_text(payload.transcription or "")
            report.report = encrypt_text(json.dumps(cleaned_report))
        db.add(report)
        db.commit()
        db.refresh(report)
        create_log(db, current_user.id, "update_report", "success")
        return _serialize_report(report)
    except Exception as exc:
        db.rollback()
        create_log(db, current_user.id, "update_report", f"failed:{exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to save report: {exc}",
        ) from exc


@router.post("/reports/save", response_model=ReportResponse)
def save_report(
    payload: ReportUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    target_id = payload.report_id
    report = db.get(Report, target_id) if target_id else None
    if report and current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    try:
        def sanitize_report(node):
            if isinstance(node, dict):
                return {str(key): sanitize_report(value) for key, value in node.items()}
            return str(node or "")

        cleaned_report = sanitize_report(payload.report)
        if not report:
            report = Report(
                user_id=current_user.id,
                transcription=encrypt_text(payload.transcription or ""),
                report=encrypt_text(json.dumps(cleaned_report)),
                audio_hash=generate_audio_hash((payload.transcription or "").encode("utf-8")),
                audio_path="manual-save",
            )
        else:
            report.transcription = encrypt_text(payload.transcription or "")
            report.report = encrypt_text(json.dumps(cleaned_report))
        db.add(report)
        db.commit()
        db.refresh(report)
        create_log(db, current_user.id, "save_report", "success")
        return _serialize_report(report)
    except Exception as exc:
        db.rollback()
        create_log(db, current_user.id, "save_report", f"failed:{exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to save report: {exc}",
        ) from exc
