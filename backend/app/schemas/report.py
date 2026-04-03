from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReportPayload(BaseModel):
    findings: str
    impression: str
    recommendations: str


class ReportResponse(BaseModel):
    id: UUID
    user_id: UUID
    transcription: str
    report: ReportPayload
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
    transcription: str
