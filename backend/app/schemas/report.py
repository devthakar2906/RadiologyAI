from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: UUID
    user_id: UUID
    transcription: str
    report: dict[str, Any]
    template: str | None = None
    formatted_report: str | None = None
    study_type: str | None = None
    audio_hash: str
    created_at: datetime


class ProcessAudioResponse(BaseModel):
    job_id: str | None = None
    status: str
    cached: bool = False
    data: ReportResponse | None = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: ReportResponse | None = None
    error: str | None = None


class TranscriptionResponse(BaseModel):
    raw_text: str
    refined_text: str
    status: str = "success"
    transcription: str


class DoctorFilterOption(BaseModel):
    id: UUID
    name: str


class ReportUpdateRequest(BaseModel):
    report_id: UUID | None = None
    transcription: str
    report: dict[str, Any]


class GenerateStructuredReportRequest(BaseModel):
    findings: str


class GenerateStructuredReportResponse(BaseModel):
    structured_json: dict[str, Any]
    formatted_report: str
    study_type: str
