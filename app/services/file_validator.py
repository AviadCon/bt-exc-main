import uuid
import os

from fastapi import UploadFile, HTTPException

from config import settings


class FileValidator:
    @staticmethod
    def validate_content_type(content_type: str):
        if not content_type:
            raise HTTPException(status_code=422, detail="Missing content type")

        if not (content_type.startswith("audio/") or content_type.startswith("video/")):
            raise HTTPException(status_code=422, detail="File must be audio or video")

    @staticmethod
    def save_file(file: UploadFile, contents: bytes) -> str:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(settings.upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        return file_path
