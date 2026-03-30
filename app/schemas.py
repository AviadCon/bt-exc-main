from typing import Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    file_name: str
    result: Optional[dict] = None
    error: Optional[str] = None


class JobListResponse(BaseModel):
    jobs: list[JobStatusResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SimpleHealthResponse(BaseModel):
    status: str
