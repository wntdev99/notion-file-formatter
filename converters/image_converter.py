import uuid
from pathlib import Path

from PIL import Image

from config import settings
from core.base_converter import AbstractConverter
from core.models import ConversionRequest, ConversionResult

_SUPPORTED_MIME = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "image/bmp", "image/tiff", "image/heic", "image/heif",
}


class ImageConverter(AbstractConverter):

    def can_handle(self, mime_type: str) -> bool:
        return mime_type in _SUPPORTED_MIME or mime_type.startswith("image/")

    def convert(self, request: ConversionRequest) -> ConversionResult:
        original_size = request.input_path.stat().st_size
        target = request.target_size_bytes

        stem = Path(request.original_filename).stem
        output_path = request.output_dir / f"{stem}_{uuid.uuid4().hex[:8]}.jpg"

        # with 문으로 PIL 이미지 명시적 해제 (메모리 누수 방지)
        with Image.open(request.input_path) as raw:
            img = raw.convert("RGB")

        attempts = 0

        try:
            # 단계 1: 품질 감소 + 크기 유지
            quality = 85
            while quality >= settings.IMAGE_MIN_QUALITY:
                img.save(output_path, format="JPEG", quality=quality, optimize=True)
                attempts += 1
                if output_path.stat().st_size <= target:
                    return ConversionResult(
                        success=True,
                        output_path=output_path,
                        original_size=original_size,
                        converted_size=output_path.stat().st_size,
                        message=f"이미지 품질 조정 완료 (quality={quality})",
                        attempts=attempts,
                    )
                quality -= settings.IMAGE_QUALITY_STEP

            # 단계 2: 해상도 축소
            w, h = img.size
            scale = 0.8
            while scale > 0.1:
                new_w = max(1, int(w * scale))
                new_h = max(1, int(h * scale))
                with img.resize((new_w, new_h), Image.LANCZOS) as resized:
                    resized.save(output_path, format="JPEG", quality=settings.IMAGE_MIN_QUALITY, optimize=True)
                attempts += 1
                if output_path.stat().st_size <= target:
                    return ConversionResult(
                        success=True,
                        output_path=output_path,
                        original_size=original_size,
                        converted_size=output_path.stat().st_size,
                        message=f"이미지 해상도 축소 완료 ({new_w}x{new_h})",
                        attempts=attempts,
                    )
                scale -= 0.1

        finally:
            img.close()

        # 파일이 생성됐다면 최종 크기 기록, 아니면 0
        final_size = output_path.stat().st_size if output_path.exists() else 0
        return ConversionResult(
            success=False,
            output_path=None,
            original_size=original_size,
            converted_size=final_size,
            message="최소 품질/크기로도 5MB 이하 달성 불가",
            attempts=attempts,
        )
