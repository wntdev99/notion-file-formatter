import magic
from pathlib import Path
from .models import FileType


_MIME_TO_FILE_TYPE: dict[str, FileType] = {}

# 이미지
for _mime in ["image/jpeg", "image/png", "image/gif", "image/webp",
              "image/bmp", "image/tiff", "image/heic", "image/heif"]:
    _MIME_TO_FILE_TYPE[_mime] = FileType.IMAGE

# PDF
_MIME_TO_FILE_TYPE["application/pdf"] = FileType.PDF

# 비디오
for _mime in ["video/mp4", "video/quicktime", "video/x-msvideo",
              "video/x-matroska", "video/webm", "video/mpeg",
              "video/3gpp", "video/x-flv"]:
    _MIME_TO_FILE_TYPE[_mime] = FileType.VIDEO


def detect_mime(path: Path) -> str:
    """파일의 실제 MIME 타입을 반환."""
    return magic.from_file(str(path), mime=True)


def detect_file_type(path: Path) -> FileType:
    """파일 타입(IMAGE / PDF / VIDEO / UNKNOWN)을 반환."""
    mime = detect_mime(path)
    if mime.startswith("image/"):
        return FileType.IMAGE
    if mime.startswith("video/"):
        return FileType.VIDEO
    return _MIME_TO_FILE_TYPE.get(mime, FileType.UNKNOWN)
