import logging
import time
from huggingface_hub import InferenceClient

from config import settings

logger = logging.getLogger(__name__)


class TranscriptExtractor:
    _last_api_call = 0
    _min_interval = 4

    def transcribe(self, audio_path: str) -> str:
        if not settings.hf_token:
            raise EnvironmentError("HF_TOKEN not configured")

        self._wait_for_rate_limit()

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

    @classmethod
    def _wait_for_rate_limit(cls):
        current_time = time.time()
        time_since_last_call = current_time - cls._last_api_call

        if time_since_last_call < cls._min_interval:
            wait_time = cls._min_interval - time_since_last_call
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s before next API call")
            time.sleep(wait_time)

        cls._last_api_call = time.time()
