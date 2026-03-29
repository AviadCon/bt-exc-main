import json
import logging
import mimetypes
import subprocess

import requests
from celery import Celery
from mongoengine import connect

from config import settings
from models import Job

logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.rabbitmq_url)


def _extract_metadata(file_path: str) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    fmt = data.get("format", {})
    return {
        "duration": float(fmt.get("duration", 0)),
        "format": fmt.get("format_name", "unknown"),
        "size_bytes": int(fmt.get("size", 0)),
    }


def _get_transcription(file_path: str) -> str | None:
    # TODO: implement this
    return None


@celery_app.task
def process_media(job_id: str, file_path: str):
    connect(host=settings.mongo_uri)

    job = Job.objects(id=job_id).first()
    if not job:
        logger.error("Job %s not found", job_id)
        return

    job.status = "processing"
    job.save()

    try:
        metadata = _extract_metadata(file_path)
        transcription = _get_transcription(file_path)

        job.result = {**metadata, "transcription": transcription}
        job.status = "completed"
        job.save()

    except Exception as e:
        logger.error("Failed to process job %s: %s", job_id, e)
