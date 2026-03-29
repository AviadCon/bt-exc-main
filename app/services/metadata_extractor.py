import json
import subprocess
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    def extract(self, file_path: str) -> dict:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", file_path],
            capture_output=True,
            text=True,
            timeout=30
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
