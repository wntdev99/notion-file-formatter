import time
import uuid
from pathlib import Path

from config import settings


class FileStorage:
    """업로드/출력 파일의 저장·조회·정리를 담당."""

    def save_upload(self, data: bytes, original_filename: str) -> tuple[str, Path]:
        """업로드 파일을 저장하고 (job_id, 저장 경로)를 반환."""
        job_id = uuid.uuid4().hex
        suffix = Path(original_filename).suffix
        dest = settings.UPLOAD_DIR / f"{job_id}{suffix}"
        dest.write_bytes(data)
        return job_id, dest

    def get_output_path(self, job_id: str) -> Path | None:
        """job_id에 해당하는 변환 결과 파일 경로를 반환."""
        for f in settings.OUTPUT_DIR.iterdir():
            if f.name.startswith(job_id):
                return f
        # job_id가 접두사가 아닌 경우도 탐색 (uuid hex 포함)
        return None

    def cleanup_expired(self) -> int:
        """만료된 임시 파일 삭제. 삭제된 파일 수 반환."""
        now = time.time()
        count = 0
        for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR]:
            for f in directory.iterdir():
                if now - f.stat().st_mtime > settings.JOB_EXPIRE_SECONDS:
                    f.unlink(missing_ok=True)
                    count += 1
        return count


file_storage = FileStorage()
