from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from backend.api.schemas import StatusResponse, UploadResponse
from backend.storage.file_storage import file_storage
from backend.worker.tasks import celery_app, convert_file
from core.models import JobStatus

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """파일 업로드 → 변환 작업 큐 투입 → job_id 반환."""
    data = await file.read()
    original_size = len(data)

    job_id, upload_path = file_storage.save_upload(data, file.filename)

    # Celery 태스크 투입 (task_id = job_id 로 고정)
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
    result = celery_app.AsyncResult(job_id)

    if result.state == "PENDING":
        return StatusResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0,
            message="대기 중...",
        )

    if result.state == "STARTED" or result.state == "PROGRESS":
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

    # FAILURE
    return StatusResponse(
        job_id=job_id,
        status=JobStatus.FAILED,
        progress=0,
        message=str(result.info),
    )


@router.get("/download/{job_id}")
def download_file(job_id: str):
    """변환된 파일 다운로드."""
    result = celery_app.AsyncResult(job_id)

    if result.state != "SUCCESS":
        raise HTTPException(status_code=404, detail="변환이 완료되지 않았습니다.")

    data = result.result
    if not data["success"] or not data["output_path"]:
        raise HTTPException(status_code=422, detail=data["message"])

    output_path = Path(data["output_path"])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="변환 파일이 만료되었습니다.")

    media_type = "application/zip" if output_path.suffix == ".zip" else "application/octet-stream"
    return FileResponse(
        path=output_path,
        filename=output_path.name,
        media_type=media_type,
    )
