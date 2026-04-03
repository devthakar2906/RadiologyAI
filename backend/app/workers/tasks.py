from uuid import UUID

from celery.utils.log import get_task_logger

from app.db.session import SessionLocal
from app.services.logging_service import create_log
from app.services.report_pipeline import process_audio_pipeline
from app.workers.celery_app import celery_app


logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def process_audio_task(self, *, audio_path: str, audio_hash: str, user_id: str):
    db = SessionLocal()
    try:
        return process_audio_pipeline(db, audio_path=audio_path, audio_hash=audio_hash, user_id=user_id)
    except Exception as exc:
        db.rollback()
        create_log(db, UUID(user_id), "process_audio", f"failed:{exc}")
        logger.exception("Audio processing failed")
        raise
    finally:
        db.close()
