import logging
from huggingface_hub import InferenceClient

from config import settings
from utils.exceptions import TranscriptFailureException

logger = logging.getLogger(__name__)


class TranscriptExtractor:
    MODEL = "openai/whisper-large-v3"
    PROVIDER = "hf-inference"

    def transcribe(self, audio_path: str) -> str:
        if not settings.hf_token:
            raise TranscriptFailureException("HF_TOKEN not configured")

        try:
            client = InferenceClient(
                provider=self.PROVIDER,
                api_key=settings.hf_token,
            )

            output = client.automatic_speech_recognition(
                audio_path,
                model=self.MODEL
            )

            return self._extract_text(output)

        except TranscriptFailureException:
            raise
        except Exception as e:
            logger.error(f"Transcript extraction failed: {e}")
            raise TranscriptFailureException(
                "Failed to extract transcript",
                original_error=e
            )

    def _extract_text(self, output) -> str:
        if hasattr(output, 'text'):
            return output.text
        if isinstance(output, dict):
            return output.get('text', '')
        return str(output)
