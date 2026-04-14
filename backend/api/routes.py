import re
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from backend.api.schemas import StatusResponse, UploadResponse
from backend.storage.file_storage import file_storage
from backend.worker.tasks import celery_app, convert_file
from config import settings
from core.models import JobStatus

router = APIRouter()

# 허용 확장자 화이트리스트
_ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".heic", ".heif",
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg", ".3gp", ".flv",
}

# job_id 형식 검증 (32자 hex)
_JOB_ID_RE = re.compile(r"^[0-9a-f]{32}$")


def _validate_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="파일명이 없습니다.")
    suffix = Path(filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"지원하지 않는 파일 형식입니다: {suffix or '(확장자 없음)'}",
        )
    return suffix


def _validate_job_id(job_id: str) -> None:
    if not _JOB_ID_RE.match(job_id):
        raise HTTPException(status_code=400, detail="잘못된 job_id 형식입니다.")


def _safe_output_path(raw_path: str) -> Path:
    """Celery 결과의 output_path가 OUTPUT_DIR 하위인지 검증 (Path Traversal 방어)."""
    path = Path(raw_path).resolve()
    allowed = settings.OUTPUT_DIR.resolve()
    if not str(path).startswith(str(allowed)):
        raise HTTPException(status_code=403, detail="접근이 허용되지 않는 경로입니다.")
    return path


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """파일 업로드 → 변환 작업 큐 투입 → job_id 반환."""
    _validate_filename(file.filename)

    try:
        job_id, upload_path = await file_storage.save_upload_stream(
            file, file.filename
        )
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))

    original_size = upload_path.stat().st_size

    convert_file.apply_async(
        args=[str(upload_path), file.filename],
        task_id=job_id,
    )

    return UploadResponse(
        job_id=job_id,
        original_filename=file.filename,
        original_size=original_size,
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str):
    """변환 작업 상태 조회."""
    _validate_job_id(job_id)
    result = celery_app.AsyncResult(job_id)

    if result.state == "PENDING":
        return StatusResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0,
            message="대기 중...",
        )

    if result.state in ("STARTED", "PROGRESS"):
        return StatusResponse(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=50,
            message="변환 중...",
        )

    if result.state == "SUCCESS":
        data = result.result
        return StatusResponse(
            job_id=job_id,
            status=JobStatus.DONE if data["success"] else JobStatus.FAILED,
            progress=100,
            message=data["message"],
            original_size=data["original_size"],
            converted_size=data["converted_size"],
            attempts=data["attempts"],
        )

    # FAILURE / REVOKED
    return StatusResponse(
        job_id=job_id,
        status=JobStatus.FAILED,
        progress=0,
        message=str(result.info) if result.info else "알 수 없는 오류",
    )


@router.get("/download/{job_id}")
def download_file(job_id: str):
    """변환된 파일 다운로드."""
    _validate_job_id(job_id)
    result = celery_app.AsyncResult(job_id)

    if result.state != "SUCCESS":
        raise HTTPException(status_code=404, detail="변환이 완료되지 않았습니다.")

    data = result.result
    if not data["success"] or not data["output_path"]:
        raise HTTPException(status_code=422, detail=data["message"])

    output_path = _safe_output_path(data["output_path"])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="변환 파일이 만료되었습니다.")

    media_type = "application/zip" if output_path.suffix == ".zip" else "application/octet-stream"
    return FileResponse(
        path=output_path,
        filename=output_path.name,
        media_type=media_type,
    )
