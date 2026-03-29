import json
import struct
import wave
from unittest.mock import MagicMock, patch

import mongomock
import mongoengine
import pytest
from fastapi.testclient import TestClient


# --------------------------------------------------------------------------- #
# Database — use mongomock so tests run without a real MongoDB                #
# --------------------------------------------------------------------------- #

@pytest.fixture(autouse=True)
def db():
    mongoengine.disconnect_all()
    mongoengine.connect(
        "testdb",
        mongo_client_class=mongomock.MongoClient,
    )
    # Prevent the Celery task from overriding the test connection when called directly
    with patch("worker.connect"):
        yield
    mongoengine.disconnect_all()


# --------------------------------------------------------------------------- #
# FastAPI test client                                                          #
# --------------------------------------------------------------------------- #

@pytest.fixture
def client():
    # Patch main.connect so the lifespan startup doesn't override the mongomock connection
    with patch("main.connect"):
        from main import app
        return TestClient(app)


# --------------------------------------------------------------------------- #
# A minimal valid WAV file — no real media tooling needed in tests            #
# --------------------------------------------------------------------------- #

@pytest.fixture
def tmp_audio(tmp_path):
    audio_file = tmp_path / "test.wav"
    with wave.open(str(audio_file), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(struct.pack("<" + "h" * 1000, *([0] * 1000)))
    fh = open(audio_file, "rb")
    yield ("test.wav", fh, "audio/wav")
    fh.close()


# --------------------------------------------------------------------------- #
# Celery — prevent real broker dispatch during upload tests                   #
# --------------------------------------------------------------------------- #

@pytest.fixture
def mock_celery():
    with patch("main.process_media") as mock_task:
        mock_task.delay = MagicMock()
        yield mock_task


# --------------------------------------------------------------------------- #
# ffprobe stubs — worker tests don't need real media files                    #
# --------------------------------------------------------------------------- #

FFPROBE_SUCCESS = json.dumps({
    "format": {"duration": "10.5", "format_name": "wav", "size": "88244"},
    "streams": [],
})


@pytest.fixture
def mock_ffprobe_ok():
    with patch("worker.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0, stdout=FFPROBE_SUCCESS, stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_ffprobe_fail():
    with patch("worker.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="No such file or directory"
        )
        yield mock_run


# --------------------------------------------------------------------------- #
# HuggingFace Whisper stub                                                    #
# --------------------------------------------------------------------------- #

@pytest.fixture
def mock_hf_whisper():
    with patch("worker._get_transcription") as mock_transcribe:
        mock_transcribe.return_value = "This is a test transcription."
        yield mock_transcribe
