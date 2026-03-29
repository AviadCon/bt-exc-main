import logging
from celery import Celery
from mongoengine import connect

from config import settings
from services.jobs.job_executor import JobExecutor

logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.rabbitmq_url)


@celery_app.task
def process_media(job_id: str, file_path: str):
    connect(host=settings.mongo_uri)

    executor = None
    try:
        executor = JobExecutor(job_id)
        executor.update_status("processing")

        result = executor.media_processor.process(file_path)
        executor.mark_as_complete(result)

    except ValueError as e:
        logger.error(f"Job not found: {e}")
    except Exception as e:
        if executor and executor.job:
            executor.mark_as_failure(f"Unexpected error: {str(e)}")
        else:
            logger.error(f"Failed to process job {job_id}: {str(e)}")
