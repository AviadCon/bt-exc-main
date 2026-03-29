import logging
from typing import Optional

from services.audio_converter import AudioConverter
from services.metadata_extractor import MetadataExtractor
from utils.transcript_extractor import TranscriptExtractor
from utils.exceptions import TranscriptFailureException, AudioExtractionException

logger = logging.getLogger(__name__)


class MediaProcessor:
    def __init__(self):
        self.audio_converter = AudioConverter()
        self.metadata_extractor = MetadataExtractor()
        self.transcript_extractor = TranscriptExtractor()
        self._temp_file: Optional[str] = None

    def process(self, file_path: str) -> dict:
        try:
            metadata = self.metadata_extractor.extract(file_path)
            transcription = self._get_transcription(file_path)
            
            return {**metadata, "transcription": transcription}
        finally:
            self._cleanup()

    def _get_transcription(self, file_path: str) -> str:
        if not self.audio_converter.needs_conversion(file_path):
            return self.transcript_extractor.transcribe(file_path)

        self._temp_file = self.audio_converter.convert_to_wav(file_path)
        return self.transcript_extractor.transcribe(self._temp_file)

    def _cleanup(self):
        if self._temp_file:
            self.audio_converter._cleanup(self._temp_file)
            self._temp_file = None
