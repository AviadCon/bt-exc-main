import uuid
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from mongoengine import connect

from config import settings
from models import Job
from worker import process_media


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(host=settings.mongo_uri)
    yield


app = FastAPI(title="Media Processing Pipeline", lifespan=lifespan)


class FileHandler:
    @staticmethod
    def validate_content_type(content_type: str):
        if not content_type:
            raise HTTPException(status_code=422, detail="Missing content type")

        if not (content_type.startswith("audio/") or content_type.startswith("video/")):
            raise HTTPException(status_code=422, detail="File must be audio or video")

    @staticmethod
    def save_file(file: UploadFile, contents: bytes) -> str:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(settings.upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        return file_path


class JobHandler:
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
    def format_response(job: Job) -> dict:
        return {
            "job_id": str(job.id),
            "status": job.status,
            "file_name": job.file_name,
            "result": job.result,
            "error": job.error,
        }


@app.post("/upload", status_code=202)
async def upload_file(file: UploadFile = File(...)):
    FileHandler.validate_content_type(file.content_type)

    contents = await file.read()
    file_path = FileHandler.save_file(file, contents)

    job = JobHandler.create_job(file.filename)
    process_media.delay(str(job.id), file_path)

    return {"job_id": str(job.id)}


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = JobHandler.get_job(job_id)
    return JobHandler.format_response(job)


@app.get("/health")
async def health():
    return {"status": "ok"}
