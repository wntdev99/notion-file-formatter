import math
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path

import pikepdf

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

        # 1단계: Ghostscript 압축 (printer → ebook → screen)
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

        # 2단계: 최고 압축으로도 초과 → 페이지 분할 후 ZIP 반환
        zip_path, num_parts, total_size = self._split_and_zip(
            output_path, request.output_dir, stem, target
        )
        attempts += num_parts

        return ConversionResult(
            success=True,
            output_path=zip_path,
            original_size=original_size,
            converted_size=total_size,
            message=f"PDF 페이지 분할 완료 ({num_parts}개 파일, ZIP 다운로드)",
            attempts=attempts,
        )

    def _split_and_zip(
        self, compressed_pdf: Path, output_dir: Path, stem: str, target: int
    ) -> tuple[Path, int, int]:
        """페이지 분할 → 각 청크 재압축 → ZIP 반환. (zip_path, 파일수, 총 크기) 반환."""
        tmp_dir = output_dir / f"_split_{uuid.uuid4().hex[:8]}"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        try:
            with pikepdf.open(compressed_pdf) as pdf:
                total_pages = len(pdf.pages)
                file_size = compressed_pdf.stat().st_size

                # 필요한 청크 수: 압축된 크기 기준으로 올림 계산 (안전 마진 20%)
                num_chunks = math.ceil(file_size / (target * 0.8))
                pages_per_chunk = math.ceil(total_pages / num_chunks)

                chunk_paths: list[Path] = []
                for i in range(num_chunks):
                    start = i * pages_per_chunk
                    end = min(start + pages_per_chunk, total_pages)

                    raw_chunk = tmp_dir / f"{stem}_part{i + 1:02d}_raw.pdf"
                    with pikepdf.new() as chunk_pdf:
                        chunk_pdf.pages.extend(pdf.pages[start:end])
                        chunk_pdf.save(raw_chunk)

                    # 각 청크를 Ghostscript screen으로 재압축
                    compressed_chunk = tmp_dir / f"{stem}_part{i + 1:02d}.pdf"
                    self._compress_gs(raw_chunk, compressed_chunk, "screen")
                    raw_chunk.unlink()
                    chunk_paths.append(compressed_chunk)

            # ZIP 묶기
            zip_path = output_dir / f"{stem}_{uuid.uuid4().hex[:8]}.zip"
            total_size = 0
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for chunk in chunk_paths:
                    zf.write(chunk, chunk.name)
                    total_size += chunk.stat().st_size

            return zip_path, len(chunk_paths), total_size

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

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
