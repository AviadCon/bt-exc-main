import logging
from app.services.jobs.models import Job
from services.media_processor import MediaProcessor

logger = logging.getLogger(__name__)


class JobExecutor:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.job = self._load(job_id)
        self.media_processor = MediaProcessor()

    def _load(self, job_id: str):
        job = Job.objects(id=job_id).first()
        if not job:
            raise ValueError(f"Job {self.job_id} not found")
        return job

    def update_status(self, status: str):
        self.job.status = status
        self.job.save()

    def mark_as_complete(self, result: dict):
        self.job.result = result
        self.job.status = "completed"
        self.job.save()
        logger.info(f"Successfully processed job {self.job_id}")

    def mark_as_failure(self, error_msg: str):
        logger.error(f"Failed to process job {self.job_id}: {error_msg}")
        self.job.status = "failed"
        self.job.error = error_msg
        self.job.save()