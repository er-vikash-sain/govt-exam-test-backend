from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "exam_prep",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.tasks.ai_tasks",
        "app.workers.tasks.email_tasks",
        "app.workers.tasks.pdf_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    "app.workers.tasks.ai_tasks.*": {"queue": "ai"},
    "app.workers.tasks.email_tasks.*": {"queue": "email"},
    "app.workers.tasks.pdf_tasks.*": {"queue": "pdf"},
}

if __name__ == "__main__":
    celery_app.start()
