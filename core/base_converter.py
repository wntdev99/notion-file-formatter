from abc import ABC, abstractmethod
from .models import ConversionRequest, ConversionResult


class AbstractConverter(ABC):
    """모든 파일 타입 컨버터가 구현해야 하는 인터페이스."""

    @abstractmethod
    def can_handle(self, mime_type: str) -> bool:
        """이 컨버터가 해당 MIME 타입을 처리할 수 있는지 여부."""
        ...

    @abstractmethod
    def convert(self, request: ConversionRequest) -> ConversionResult:
        """파일을 target_size_bytes 이하로 변환."""
        ...
