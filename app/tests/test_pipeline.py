"""
Media Pipeline — Exercise Test Suite
=====================================

Run with:  poetry run pytest

Starting state: 5 FAILING, 1 PASSING.
Goal:           all 6 green + the HuggingFace integration wired up.

Do NOT modify this file.
"""

import pytest
from models import Job


# ------------------------------------------------------------------ #
# 1. Upload endpoint returns a job_id that exists in the database     #
#    Fails because of BUG 1 in main.py                                #
# ------------------------------------------------------------------ #

def test_upload_returns_valid_job_id(client, tmp_audio, mock_celery):
    response = client.post("/upload", files={"file": tmp_audio})

    assert response.status_code == 202, "Expected HTTP 202 Accepted"
    job_id = response.json().get("job_id")
    assert job_id, "Response must include a 'job_id' field"

    job = Job.objects(id=job_id).first()
    assert job is not None, (
        f"job_id '{job_id}' was returned but no matching job exists in the database. "
        "Hint: check what value is being returned from the upload endpoint."
    )


# ------------------------------------------------------------------ #
# 2. GET /jobs/{id} returns the correct job                           #
#    Fails because of BUG 3 in main.py                                #
# ------------------------------------------------------------------ #

def test_get_job_returns_correct_job(client):
    # Two jobs with the same filename — a query by filename would be ambiguous
    completed = Job(file_name="video.mp4", status="completed", result={"duration": 10.0}).save()
    Job(file_name="video.mp4", status="pending").save()

    response = client.get(f"/jobs/{completed.id}")

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. "
        "Hint: check which field the endpoint uses to look up the job."
    )
    assert response.json()["status"] == "completed", (
        "Returned job does not match the requested ID. "
        "Hint: jobs must be looked up by their primary key, not by filename."
    )


# ------------------------------------------------------------------ #
# 3. Failed jobs are stored as 'failed', not stuck in 'processing'   #
#    Fails because of BUG 2 in worker.py                              #
# ------------------------------------------------------------------ #

def test_failed_job_is_marked_failed(mock_ffprobe_fail):
    from worker import process_media

    job = Job(file_name="corrupt.mp4", status="pending").save()
    process_media(str(job.id), "/tmp/nonexistent.mp4")

    job.reload()
    assert job.status == "failed", (
        f"Expected status='failed', got '{job.status}'. "
        "Hint: when an exception is raised in the worker, the job must be updated accordingly."
    )
    assert job.error, "job.error should contain the error message"


# ------------------------------------------------------------------ #
# 4. Job result includes a transcription from HuggingFace Whisper     #
#    Fails because _get_transcription() is not yet implemented        #
# ------------------------------------------------------------------ #

def test_transcription_attached_to_completed_job(mock_ffprobe_ok):
    """
    This test does NOT mock _get_transcription — you must implement it.

    Requirements:
    - Call the HuggingFace Inference API (openai/whisper-large-v3)
    - Attach the returned text to job.result["transcription"]
    - If HF_TOKEN is not set, it is acceptable to skip (return None)
      but the job must still complete successfully with the other metadata.

    For this test to pass, set HF_TOKEN in your .env and make a real API call.
    """
    from worker import process_media

    job = Job(file_name="interview.wav", status="pending").save()
    process_media(str(job.id), "/fake/interview.wav")

    job.reload()
    assert job.status == "completed", f"Job failed with error: {job.error}"
    assert job.result.get("transcription") is not None, (
        "job.result['transcription'] is None. "
        "Implement _get_transcription() in worker.py to call the HuggingFace Whisper API."
    )


# ------------------------------------------------------------------ #
# 5. Job query is indexed — no full collection scans                  #
#    Fails because of BUG 3 (file_name has no index, id does)         #
# ------------------------------------------------------------------ #

def test_job_lookup_uses_primary_key(client):
    job = Job(file_name="sample.mp3", status="completed", result={"duration": 5.0}).save()

    response = client.get(f"/jobs/{job.id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == str(job.id), (
        "The returned job_id does not match the requested one. "
        "Ensure the endpoint queries by document ID, not by any other field."
    )


# ------------------------------------------------------------------ #
# 6. Non-media uploads are rejected — PASSES from the start          #
#    Leave this here so candidates know something works correctly     #
# ------------------------------------------------------------------ #

def test_upload_invalid_file_returns_422(client):
    response = client.post(
        "/upload",
        files={"file": ("report.pdf", b"%PDF fake", "application/pdf")},
    )
    assert response.status_code == 422
