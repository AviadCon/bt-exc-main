import os
import subprocess
import tempfile
import logging
from typing import Optional

from utils.exceptions import AudioExtractionException

logger = logging.getLogger(__name__)


class AudioConverter:
    WHISPER_SAMPLE_RATE = 16000
    AUDIO_CODEC = "pcm_s16le"
    CHANNELS = 1

    def is_audio_file(self, file_path: str) -> bool:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0", 
             "-show_entries", "stream=codec_type", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0 and "audio" in result.stdout

    def needs_conversion(self, file_path: str) -> bool:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name,sample_rate,channels",
             "-of", "default=noprint_wrappers=1", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return True
            
        output = result.stdout.lower()
        return not (f"sample_rate={self.WHISPER_SAMPLE_RATE}" in output and 
                   f"channels={self.CHANNELS}" in output and
                   "codec_name=pcm_s16le" in output)

    def convert_to_wav(self, file_path: str) -> str:
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()

        try:
            result = subprocess.run(
                ["ffmpeg", "-i", file_path, "-vn",
                 "-acodec", self.AUDIO_CODEC,
                 "-ar", str(self.WHISPER_SAMPLE_RATE),
                 "-ac", str(self.CHANNELS),
                 "-y", temp_audio_path],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise AudioExtractionException(
                    f"FFmpeg conversion failed",
                    original_error=RuntimeError(result.stderr)
                )

            return temp_audio_path

        except AudioExtractionException:
            self._cleanup(temp_audio_path)
            raise
        except Exception as e:
            self._cleanup(temp_audio_path)
            raise AudioExtractionException(
                f"Audio conversion failed",
                original_error=e
            )

    def _cleanup(self, file_path: Optional[str]):
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
