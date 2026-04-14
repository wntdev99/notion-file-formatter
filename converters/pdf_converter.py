import shutil
import subprocess
import uuid
from pathlib import Path

from config import settings
from core.base_converter import AbstractConverter
from core.models import ConversionRequest, ConversionResult

# Ghostscript PDF 품질 단계 (높을수록 압축률 높음)
_GS_SETTINGS = ["printer", "ebook", "screen"]


class PDFConverter(AbstractConverter):

    def can_handle(self, mime_type: str) -> bool:
        return mime_type == "application/pdf"

    def convert(self, request: ConversionRequest) -> ConversionResult:
        original_size = request.input_path.stat().st_size
        target = request.target_size_bytes

        stem = Path(request.original_filename).stem
        output_path = request.output_dir / f"{stem}_{uuid.uuid4().hex[:8]}.pdf"

        attempts = 0

        for gs_setting in _GS_SETTINGS:
            self._compress_gs(request.input_path, output_path, gs_setting)
            attempts += 1
            converted_size = output_path.stat().st_size

            if converted_size <= target:
                return ConversionResult(
                    success=True,
                    output_path=output_path,
                    original_size=original_size,
                    converted_size=converted_size,
                    message=f"PDF 압축 완료 (품질={gs_setting})",
                    attempts=attempts,
                )

        return ConversionResult(
            success=False,
            output_path=None,
            original_size=original_size,
            converted_size=output_path.stat().st_size,
            message="PDF를 5MB 이하로 압축할 수 없습니다. 페이지 분할을 고려하세요.",
            attempts=attempts,
        )

    def _compress_gs(self, input_path: Path, output_path: Path, setting: str) -> None:
        subprocess.run(
            [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS=/{setting}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_path}",
                str(input_path),
            ],
            check=True,
        )
