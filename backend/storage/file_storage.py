from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from config import settings

if TYPE_CHECKING:
    from fastapi import UploadFile


class FileStorage:
    """업로드/출력 파일의 저장·조회·정리를 담당."""

    async def save_upload_stream(
        self, upload_file: "UploadFile", original_filename: str
    ) -> tuple[str, Path]:
        """청크 스트리밍으로 저장하여 메모리 직접 로드를 방지. (job_id, 저장 경로) 반환."""
        job_id = uuid.uuid4().hex
        suffix = Path(original_filename).suffix.lower()
        dest = settings.UPLOAD_DIR / f"{job_id}{suffix}"

        total = 0
        with dest.open("wb") as f:
            while chunk := await upload_file.read(1024 * 1024):  # 1MB 청크
                total += len(chunk)
                if total > settings.MAX_UPLOAD_BYTES:
                    dest.unlink(missing_ok=True)
                    raise ValueError(
                        f"파일 크기가 허용 한도({settings.MAX_UPLOAD_BYTES // (1024 ** 3)}GB)를 초과했습니다."
                    )
                f.write(chunk)

        return job_id, dest

    def cleanup_expired(self) -> int:
        """만료된 임시 파일 삭제. 삭제된 파일 수 반환."""
        now = time.time()
        count = 0
        for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR]:
            for f in directory.iterdir():
                if f.is_file() and now - f.stat().st_mtime > settings.JOB_EXPIRE_SECONDS:
                    f.unlink(missing_ok=True)
                    count += 1
        return count


file_storage = FileStorage()
