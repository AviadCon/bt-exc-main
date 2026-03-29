import logging
from huggingface_hub import InferenceClient

from config import settings

logger = logging.getLogger(__name__)


class TranscriptExtractor:

    def transcribe(self, audio_path: str) -> str:
        if not settings.hf_token:
            raise EnvironmentError("HF_TOKEN not configured")
        try:
            client = InferenceClient(
                provider="hf-inference",
                api_key=settings.hf_token,
            )
            output = client.automatic_speech_recognition(
                audio_path,
                model="openai/whisper-large-v3"
            )
            return output.text
        except Exception as e:
            logger.error(f"Transcript extraction failed: {e}")
            raise EnvironmentError(f"Transcript extraction failed: {e}")
