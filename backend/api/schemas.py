from pydantic import BaseModel
from core.models import JobStatus


class UploadResponse(BaseModel):
    job_id: str
    original_filename: str
    original_size: int
    message: str = "변환 작업이 시작되었습니다."


class StatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int  # 0 ~ 100
    message: str
    original_size: int | None = None
    converted_size: int | None = None
    attempts: int | None = None


class ErrorResponse(BaseModel):
    detail: str
