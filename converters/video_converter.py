import uuid
from pathlib import Path

import ffmpeg

from config import settings
from core.base_converter import AbstractConverter
from core.models import ConversionRequest, ConversionResult

_SUPPORTED_MIME = {
    "video/mp4", "video/quicktime", "video/x-msvideo",
    "video/x-matroska", "video/webm", "video/mpeg",
    "video/3gpp", "video/x-flv",
}


class VideoConverter(AbstractConverter):

    def can_handle(self, mime_type: str) -> bool:
        return mime_type in _SUPPORTED_MIME or mime_type.startswith("video/")

    def convert(self, request: ConversionRequest) -> ConversionResult:
        original_size = request.input_path.stat().st_size
        target = request.target_size_bytes

        stem = Path(request.original_filename).stem
        output_path = request.output_dir / f"{stem}_{uuid.uuid4().hex[:8]}.mp4"

        # 원본 비디오 정보 조회 (손상 파일 방어)
        try:
            probe = ffmpeg.probe(str(request.input_path))
            video_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "video"), None
            )
            original_height = int(video_stream["height"]) if video_stream else 1080
        except ffmpeg.Error as e:
            return ConversionResult(
                success=False,
                output_path=None,
                original_size=original_size,
                converted_size=0,
                message=f"비디오 파일을 읽을 수 없습니다: {e.stderr.decode(errors='ignore') if e.stderr else str(e)}",
            )

        # 원본 이하 해상도만 필터링. 목록에 없는 해상도(예: 300p)는 원본 그대로 추가
        candidate_res = sorted(
            {r for r in settings.VIDEO_RESOLUTIONS if r <= original_height} | {original_height},
            reverse=True,
        )

        attempts = 0

        for crf in range(settings.VIDEO_CRF_START, settings.VIDEO_CRF_MAX + 1, settings.VIDEO_CRF_STEP):
            for res in candidate_res:
                try:
                    self._encode(request.input_path, output_path, crf, res)
                except ffmpeg.Error as e:
                    return ConversionResult(
                        success=False,
                        output_path=None,
                        original_size=original_size,
                        converted_size=0,
                        message=f"인코딩 실패: {e.stderr.decode(errors='ignore') if e.stderr else str(e)}",
                    )
                attempts += 1
                converted_size = output_path.stat().st_size

                if converted_size <= target:
                    return ConversionResult(
                        success=True,
                        output_path=output_path,
                        original_size=original_size,
                        converted_size=converted_size,
                        message=f"비디오 변환 완료 (CRF={crf}, {res}p)",
                        attempts=attempts,
                    )

        return ConversionResult(
            success=False,
            output_path=None,
            original_size=original_size,
            converted_size=output_path.stat().st_size if output_path.exists() else 0,
            message="비디오를 5MB 이하로 압축할 수 없습니다.",
            attempts=attempts,
        )

    def _encode(self, input_path: Path, output_path: Path, crf: int, height: int) -> None:
        if output_path.exists():
            output_path.unlink()
        (
            ffmpeg
            .input(str(input_path))
            .output(
                str(output_path),
                vcodec="libx264",
                crf=crf,
                vf=f"scale=-2:{height}",
                acodec="aac",
                audio_bitrate="96k",
                preset="fast",
                movflags="+faststart",
            )
            .overwrite_output()
            .run(quiet=True)
        )
