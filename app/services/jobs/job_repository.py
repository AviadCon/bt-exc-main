from fastapi import HTTPException

from app.services.jobs.models import Job


class JobRepository:
    @staticmethod
    def create_job(filename: str) -> Job:
        job = Job(file_name=filename, status="pending")
        job.save()
        return job

    @staticmethod
    def get_job(job_id: str) -> Job:
        job = Job.objects(id=job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return job
