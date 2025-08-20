from celery import Celery
from app.core.config import settings


celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

import app.services.resume_service
import app.services.llm_service
import app.services.zoom_service