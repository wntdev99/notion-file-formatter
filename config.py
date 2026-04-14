from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 파일 크기 제한 (Notion 5MB)
    TARGET_SIZE_BYTES: int = 5 * 1024 * 1024

    # 파일 저장 경로
    UPLOAD_DIR: Path = Path("storage/uploads")
    OUTPUT_DIR: Path = Path("storage/outputs")

    # 작업 만료 시간 (초) - 1시간 후 자동 삭제
    JOB_EXPIRE_SECONDS: int = 3600

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # 변환 재시도 횟수
    MAX_RETRY: int = 5

    # 이미지 변환 설정
    IMAGE_MIN_QUALITY: int = 10
    IMAGE_QUALITY_STEP: int = 10
    IMAGE_MAX_DIMENSION: int = 4096

    # PDF 변환 설정
    PDF_IMAGE_DPI: int = 150
    PDF_MIN_IMAGE_DPI: int = 72

    # 비디오 변환 설정
    VIDEO_CRF_START: int = 28
    VIDEO_CRF_MAX: int = 51
    VIDEO_CRF_STEP: int = 4
    VIDEO_RESOLUTIONS: list = [1080, 720, 480, 360]

    class Config:
        env_file = ".env"


settings = Settings()

# 저장 디렉토리 자동 생성
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
