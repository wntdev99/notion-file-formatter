from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class FileType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class ConversionRequest:
    input_path: Path
    output_dir: Path
    target_size_bytes: int
    original_filename: str


@dataclass
class ConversionResult:
    success: bool
    output_path: Path | None
    original_size: int
    converted_size: int
    message: str
    attempts: int = 0
