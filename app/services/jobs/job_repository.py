import math
from fastapi import HTTPException

from models import Job
from schemas import JobListResponse, JobStatusResponse


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

    @staticmethod
    def list_jobs(page: int = 1, page_size: int = 10) -> JobListResponse:
        # Get total count
        total = Job.objects.count()

        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        # Get jobs ordered by created_at descending (most recent first)
        jobs = Job.objects.order_by('-created_at').skip(skip).limit(page_size)

        # Convert to response format
        job_responses = [
            JobStatusResponse(
                job_id=str(job.id),
                status=job.status,
                file_name=job.file_name,
                result=job.result,
                error=job.error
            )
            for job in jobs
        ]

        return JobListResponse(
            jobs=job_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
