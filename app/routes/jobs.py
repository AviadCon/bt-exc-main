from fastapi import APIRouter, UploadFile, File, Query

from schemas import UploadResponse, JobStatusResponse, JobListResponse
from services.file_validator import FileValidator
from services.jobs.job_repository import JobRepository
from worker import process_media

router = APIRouter(tags=["jobs"])


@router.post("/upload", status_code=202, response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    FileValidator.validate_content_type(file.content_type)

    contents = await file.read()
    file_path = FileValidator.save_file(file, contents)

    job = JobRepository.create_job(file.filename)
    process_media.delay(str(job.id), file_path)

    return UploadResponse(job_id=str(job.id))


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
) -> JobListResponse:
    return JobRepository.list_jobs(page=page, page_size=page_size)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = JobRepository.get_job(job_id)
    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        file_name=job.file_name,
        result=job.result,
        error=job.error
    )
