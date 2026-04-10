from uuid import UUID

from celery.utils.log import get_task_logger
import httpx

from app.db.session import SessionLocal
from app.services.logging_service import create_log
from app.services.report_pipeline import process_audio_pipeline, process_transcription_pipeline
from app.workers.celery_app import celery_app


logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(httpx.HTTPError, RuntimeError, TimeoutError),
    retry_backoff=5,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
)
def process_audio_task(self, *, audio_path: str, audio_hash: str, user_id: str):
    db = SessionLocal()
    try:
        import asyncio

        logger.info("Starting audio processing task for user=%s hash=%s", user_id, audio_hash)
        create_log(db, UUID(user_id), "process_audio", "started")
        return asyncio.run(process_audio_pipeline(db, audio_path=audio_path, audio_hash=audio_hash, user_id=user_id))
    except Exception as exc:
        db.rollback()
        create_log(db, UUID(user_id), "process_audio", f"failed:{exc}")
        logger.exception("Audio processing failed")
        raise
    finally:
        db.close()


@celery_app.task(
    bind=True,
    autoretry_for=(httpx.HTTPError, RuntimeError, TimeoutError),
    retry_backoff=5,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
)
def process_text_task(self, *, transcription: str, audio_hash: str, user_id: str):
    db = SessionLocal()
    try:
        import asyncio

        logger.info("Starting text report task for user=%s hash=%s", user_id, audio_hash)
        create_log(db, UUID(user_id), "process_text_report", "started")
        return asyncio.run(
            process_transcription_pipeline(
                db,
                transcription=transcription,
                audio_hash=audio_hash,
                user_id=user_id,
                audio_path="manual-text",
            )
        )
    except Exception as exc:
        db.rollback()
        create_log(db, UUID(user_id), "process_text_report", f"failed:{exc}")
        logger.exception("Text report processing failed")
        raise
    finally:
        db.close()
