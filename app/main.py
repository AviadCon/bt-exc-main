from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File
from mongoengine import connect
from pydantic import BaseModel

from config import settings
from services.file_validator import FileValidator
from services.health_checker import HealthChecker, HealthResponse
from services.jobs.job_repository import JobRepository
from worker import process_media


class UploadResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    file_name: str
    result: Optional[dict] = None
    error: Optional[str] = None


class SimpleHealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(host=settings.mongo_uri)
    yield


app = FastAPI(title="Media Processing Pipeline", lifespan=lifespan)


@app.post("/upload", status_code=202, response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    FileValidator.validate_content_type(file.content_type)

    contents = await file.read()
    file_path = FileValidator.save_file(file, contents)

    job = JobRepository.create_job(file.filename)
    process_media.delay(str(job.id), file_path)

    return UploadResponse(job_id=str(job.id))


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = JobRepository.get_job(job_id)
    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        file_name=job.file_name,
        result=job.result,
        error=job.error
    )


@app.get("/health", response_model=SimpleHealthResponse)
async def health() -> SimpleHealthResponse:
    return SimpleHealthResponse(status="ok")


@app.get("/health/rabbitmq", response_model=HealthResponse)
async def health_rabbitmq() -> HealthResponse:
    return HealthChecker.rabbit()


@app.get("/health/mongodb", response_model=HealthResponse)
async def health_mongodb() -> HealthResponse:
    return HealthChecker.mongo()
