import uuid
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from mongoengine import connect

from config import settings
from models import Job
from worker import process_media

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(host=settings.mongo_uri)
    yield


app = FastAPI(title="Media Processing Pipeline", lifespan=lifespan)


@app.post("/upload", status_code=202)
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type or not (
        file.content_type.startswith("audio/") or file.content_type.startswith("video/")
    ):
        raise HTTPException(status_code=422, detail="File must be audio or video")

    contents = await file.read()

    file_path = os.path.join(settings.upload_dir, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)

    job = Job(file_name=file.filename, status="pending")
    job.save()

    process_media.delay(str(job.id), file_path)

    return {"job_id": str(uuid.uuid4())}


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = Job.objects(file_name=job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": str(job.id),
        "status": job.status,
        "file_name": job.file_name,
        "result": job.result,
        "error": job.error,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
