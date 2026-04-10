from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "radiology_ai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    imports=("app.workers.tasks",),
    accept_content=["json"],
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    broker_pool_limit=20,
    result_expires=86400,
    worker_send_task_events=True,
    task_send_sent_event=True,
    worker_max_tasks_per_child=100,
)
