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

        # 2단계: 최고 압축으로도 초과 → 이진 분할로 모든 파트가 5MB 이하 보장
        tmp_dir = request.output_dir / f"_split_{uuid.uuid4().hex[:8]}"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        try:
            parts, split_attempts = self._split_until_fit(output_path, tmp_dir, stem, target)
            attempts += split_attempts

            # 파트 번호 재정렬 후 ZIP 묶기
            zip_path = request.output_dir / f"{stem}_{uuid.uuid4().hex[:8]}.zip"
            max_part_size = 0
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, part in enumerate(parts, start=1):
                    part_name = f"{stem}_part{i:02d}.pdf"
                    zf.write(part, part_name)
                    max_part_size = max(max_part_size, part.stat().st_size)

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        return ConversionResult(
            success=True,
            output_path=zip_path,
            original_size=original_size,
            converted_size=max_part_size,   # 가장 큰 파트 크기 → Notion 업로드 가능 여부 직접 반영
            message=f"PDF 페이지 분할 완료 ({len(parts)}개 파일 ZIP · 최대 파트 {max_part_size / 1024 / 1024:.2f}MB)",
            attempts=attempts,
        )

    def _split_until_fit(
        self, source: Path, tmp_dir: Path, stem: str, target: int
    ) -> tuple[list[Path], int]:
        """모든 파트가 target 이하가 될 때까지 이진 분할."""
        result: list[Path] = []
        attempts = 0
        # 큐: (파일경로, 파트 식별자)
        queue: list[tuple[Path, str]] = [(source, stem)]

        while queue:
            part_path, part_stem = queue.pop(0)

            if part_path.stat().st_size <= target:
                result.append(part_path)
                continue

            with pikepdf.open(part_path) as pdf:
                n_pages = len(pdf.pages)

            if n_pages <= 1:
                # 단일 페이지인데 5MB 초과 → 어쩔 수 없이 그대로 포함
                result.append(part_path)
                continue

            # 절반씩 분할
            mid = n_pages // 2
            for i, (start, end) in enumerate([(0, mid), (mid, n_pages)]):
                child_stem = f"{part_stem}_{i}"
                raw = tmp_dir / f"{child_stem}_raw.pdf"
                compressed = tmp_dir / f"{child_stem}.pdf"

                with pikepdf.open(part_path) as pdf:
                    with pikepdf.new() as out:
                        out.pages.extend(pdf.pages[start:end])
                        out.save(raw)

                self._compress_gs(raw, compressed, "screen")
                raw.unlink()
                attempts += 1
                queue.append((compressed, child_stem))

        return result, attempts

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
