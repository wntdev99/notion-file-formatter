from pathlib import Path

from config import settings
from .converter_registry import ConverterRegistry
from .file_detector import detect_mime
from .models import ConversionRequest, ConversionResult


class ConversionPipeline:
    """파일 변환 전체 흐름을 조율하는 파이프라인."""

    def __init__(self, registry: ConverterRegistry) -> None:
        self._registry = registry

    def run(self, input_path: Path, original_filename: str) -> ConversionResult:
        input_size = input_path.stat().st_size

        # 이미 5MB 이하이면 변환 불필요
        if input_size <= settings.TARGET_SIZE_BYTES:
            return ConversionResult(
                success=True,
                output_path=input_path,
                original_size=input_size,
                converted_size=input_size,
                message="변환 불필요 (이미 5MB 이하)",
            )

        mime_type = detect_mime(input_path)

        try:
            converter = self._registry.get_converter(mime_type)
        except ValueError as e:
            return ConversionResult(
                success=False,
                output_path=None,
                original_size=input_size,
                converted_size=0,
                message=str(e),
            )

        request = ConversionRequest(
            input_path=input_path,
            output_dir=settings.OUTPUT_DIR,
            target_size_bytes=settings.TARGET_SIZE_BYTES,
            original_filename=original_filename,
        )

        return converter.convert(request)
