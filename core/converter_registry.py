from .base_converter import AbstractConverter


class ConverterRegistry:
    """MIME 타입을 기반으로 적합한 Converter를 찾아주는 레지스트리."""

    def __init__(self) -> None:
        self._converters: list[AbstractConverter] = []

    def register(self, converter: AbstractConverter) -> None:
        self._converters.append(converter)

    def get_converter(self, mime_type: str) -> AbstractConverter:
        for converter in self._converters:
            if converter.can_handle(mime_type):
                return converter
        raise ValueError(f"지원하지 않는 파일 형식입니다: {mime_type}")
