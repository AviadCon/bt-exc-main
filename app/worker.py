import logging
from celery import Celery
from mongoengine import connect

from config import settings
from services.job_processor import JobProcessor

logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.rabbitmq_url)


@celery_app.task
def process_media(job_id: str, file_path: str):
    connect(host=settings.mongo_uri)

    job = None
    try:
        job = JobProcessor(job_id)
        job.update_status("processing")

        result = job.media_processor.process(file_path)
        job.mark_as_complete(result)

    except ValueError as e:
        logger.error(f"Job not found: {e}")
    except Exception as e:
        if job and job.job:
            job.mark_as_failure(f"Unexpected error: {str(e)}")
        else:
            logger.error(f"Failed to process job {job_id}: {str(e)}")
