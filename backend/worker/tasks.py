from datetime import timedelta
from pathlib import Path

from celery import Celery

from config import settings
from converters.image_converter import ImageConverter
from converters.pdf_converter import PDFConverter
from converters.video_converter import VideoConverter
from core.converter_registry import ConverterRegistry
from core.pipeline import ConversionPipeline

# Celery 앱 초기화
celery_app = Celery("notion_formatter", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=settings.JOB_EXPIRE_SECONDS,
    # 변환 작업 타임아웃: 소프트 10분, 하드 12분
    task_soft_time_limit=600,
    task_time_limit=720,
    # 만료 파일 주기적 정리 (1시간마다)
    beat_schedule={
        "cleanup-expired-files": {
            "task": "cleanup_expired_files",
            "schedule": timedelta(hours=1),
        }
    },
    broker_connection_retry_on_startup=True,
)

# 컨버터 등록 (새 타입 추가 시 여기에 한 줄 추가)
_registry = ConverterRegistry()
_registry.register(ImageConverter())
_registry.register(PDFConverter())
_registry.register(VideoConverter())

_pipeline = ConversionPipeline(_registry)


@celery_app.task(name="cleanup_expired_files")
def cleanup_expired_files() -> dict:
    """만료된 임시 파일을 주기적으로 삭제 (Celery beat 호출)."""
    from backend.storage.file_storage import file_storage
    count = file_storage.cleanup_expired()
    return {"deleted": count}


@celery_app.task(bind=True, name="convert_file")
def convert_file(self, upload_path: str, original_filename: str) -> dict:
    """
    반환값 형식:
    {
        "success": bool,
        "output_path": str | None,
        "original_size": int,
        "converted_size": int,
        "message": str,
        "attempts": int,
    }
    """
    result = _pipeline.run(
        input_path=Path(upload_path),
        original_filename=original_filename,
    )
    return {
        "success": result.success,
        "output_path": str(result.output_path) if result.output_path else None,
        "original_size": result.original_size,
        "converted_size": result.converted_size,
        "message": result.message,
        "attempts": result.attempts,
    }
