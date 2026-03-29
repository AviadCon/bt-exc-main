import logging
from celery import Celery
from mongoengine import connect

from config import settings
from models import Job
from services.media_processor import MediaProcessor
from utils.exceptions import TranscriptFailureException, AudioExtractionException

logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.rabbitmq_url)


class JobProcessor:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.job = None
        self.media_processor = MediaProcessor()

    def execute(self, file_path: str):
        self._load_job()
        self._update_status("processing")

        try:
            result = self.media_processor.process(file_path)
            self._complete_job(result)
        except (TranscriptFailureException, AudioExtractionException) as e:
            self._fail_job(str(e))
        except Exception as e:
            self._fail_job(f"Unexpected error: {str(e)}")

    def _load_job(self):
        self.job = Job.objects(id=self.job_id).first()
        if not self.job:
            raise ValueError(f"Job {self.job_id} not found")

    def _update_status(self, status: str):
        self.job.status = status
        self.job.save()

    def _complete_job(self, result: dict):
        self.job.result = result
        self.job.status = "completed"
        self.job.save()
        logger.info(f"Successfully processed job {self.job_id}")

    def _fail_job(self, error_msg: str):
        logger.error(f"Failed to process job {self.job_id}: {error_msg}")
        self.job.status = "failed"
        self.job.error = error_msg
        self.job.save()


@celery_app.task
def process_media(job_id: str, file_path: str):
    connect(host=settings.mongo_uri)

    try:
        processor = JobProcessor(job_id)
        processor.execute(file_path)
    except ValueError as e:
        logger.error(str(e))