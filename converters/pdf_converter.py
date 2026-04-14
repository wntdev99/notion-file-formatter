import uuid
from pathlib import Path

import pikepdf

from config import settings
from core.base_converter import AbstractConverter
from core.models import ConversionRequest, ConversionResult


class PDFConverter(AbstractConverter):

    def can_handle(self, mime_type: str) -> bool:
        return mime_type == "application/pdf"

    def convert(self, request: ConversionRequest) -> ConversionResult:
        original_size = request.input_path.stat().st_size
        target = request.target_size_bytes

        stem = Path(request.original_filename).stem
        output_path = request.output_dir / f"{stem}_{uuid.uuid4().hex[:8]}.pdf"

        attempts = 0
        dpi = settings.PDF_IMAGE_DPI

        while dpi >= settings.PDF_MIN_IMAGE_DPI:
            self._compress(request.input_path, output_path, dpi)
            attempts += 1
            converted_size = output_path.stat().st_size

            if converted_size <= target:
                return ConversionResult(
                    success=True,
                    output_path=output_path,
                    original_size=original_size,
                    converted_size=converted_size,
                    message=f"PDF 압축 완료 (DPI={dpi})",
                    attempts=attempts,
                )
            dpi = max(settings.PDF_MIN_IMAGE_DPI, dpi - 25)
            if dpi == settings.PDF_MIN_IMAGE_DPI and converted_size > target:
                break

        return ConversionResult(
            success=False,
            output_path=None,
            original_size=original_size,
            converted_size=output_path.stat().st_size,
            message="PDF를 5MB 이하로 압축할 수 없습니다. 페이지 분할을 고려하세요.",
            attempts=attempts,
        )

    def _compress(self, input_path: Path, output_path: Path, dpi: int) -> None:
        with pikepdf.open(input_path) as pdf:
            pdf.save(
                output_path,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                recompress_flate=True,
            )
