"""Video metadata extraction and integrity inspection using OpenCV."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict

import cv2

from clipmind.config import config
from clipmind.exceptions import CorruptedVideoError, SecurityValidationError
from clipmind.logger import logger


@dataclass
class VideoMetadata:
    """Detailed structural metadata for a video file."""

    filename: str
    file_size_bytes: int
    file_size_mb: float
    width: int
    height: int
    fps: float
    total_frames: int
    duration_seconds: float
    duration_formatted: str
    aspect_ratio: str
    fourcc_codec: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for export and reporting."""
        return asdict(self)


def format_duration(seconds: float) -> str:
    """Formats duration in seconds to standard HH:MM:SS or MM:SS format."""
    total_sec = max(0, int(round(seconds)))
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    sec = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def calculate_aspect_ratio(width: int, height: int) -> str:
    """Calculates simplified aspect ratio string (e.g., '16:9', '4:3', '1:1')."""
    if width <= 0 or height <= 0:
        return "Unknown"
    gcd = math.gcd(width, height)
    num, den = width // gcd, height // gcd

    # Standard approximation mappings
    ratio = width / height
    if abs(ratio - 16 / 9) < 0.05:
        return "16:9 (Widescreen)"
    if abs(ratio - 9 / 16) < 0.05:
        return "9:16 (Vertical)"
    if abs(ratio - 4 / 3) < 0.05:
        return "4:3 (Standard)"
    if abs(ratio - 1.0) < 0.02:
        return "1:1 (Square)"
    if abs(ratio - 21 / 9) < 0.05:
        return "21:9 (Ultrawide)"

    return f"{num}:{den}"


def decode_fourcc(fourcc_int: float) -> str:
    """Decodes OpenCV FourCC integer to human-readable string."""
    try:
        val = int(fourcc_int)
        chars = [chr((val >> 8 * i) & 0xFF) for i in range(4)]
        codec = "".join(chars).strip()
        return codec if codec.isprintable() and len(codec) > 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def extract_video_metadata(video_path: Path) -> VideoMetadata:
    """Extracts structural metadata from a video file and validates its decodability.

    Raises:
        CorruptedVideoError: If video cannot be opened or decoded by OpenCV.
        SecurityValidationError: If video duration exceeds configured limits.
    """
    path = Path(video_path).resolve()
    if not path.is_file():
        raise CorruptedVideoError(f"Video file not found at path: {path}")

    file_size_bytes = path.stat().st_size
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise CorruptedVideoError(
                f"OpenCV could not open video stream for {path.name}",
                user_friendly_message="The video file could not be opened. It may be corrupt or encoded in an unsupported codec.",
            )

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = decode_fourcc(cap.get(cv2.CAP_PROP_FOURCC))

        # Sanity check properties
        if width <= 0 or height <= 0:
            raise CorruptedVideoError(
                f"Invalid video dimensions: {width}x{height}",
                user_friendly_message="Video has invalid resolution dimensions and cannot be processed.",
            )

        if width > config.max_frame_dimension or height > config.max_frame_dimension:
            raise SecurityValidationError(
                f"Video resolution {width}x{height} exceeds maximum allowed {config.max_frame_dimension}px.",
                user_friendly_message=f"Video resolution ({width}x{height}) is too large. Maximum supported dimension is {config.max_frame_dimension}px.",
            )

        # Fallback for FPS if missing or anomalous
        if fps <= 0.0 or math.isnan(fps) or fps > 240.0:
            logger.warning("Unusual FPS reported (%s), defaulting to 30.0", fps)
            fps = 30.0

        # Attempt to decode the very first frame to confirm decodability
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            raise CorruptedVideoError(
                "Unable to read the first frame from the video stream.",
                user_friendly_message="Unable to decode any frames from the uploaded video. The video stream appears corrupted.",
            )

        # If total_frames was 0 or negative, we compute approximate or at least 1
        if total_frames <= 0:
            total_frames = 1

        duration_seconds = total_frames / fps
        if duration_seconds > config.max_video_duration_seconds:
            raise SecurityValidationError(
                f"Video duration ({duration_seconds:.1f}s) exceeds limit of {config.max_video_duration_seconds}s.",
                user_friendly_message=f"Video duration is {format_duration(duration_seconds)}, which exceeds the limit of {format_duration(config.max_video_duration_seconds)}.",
            )

        duration_formatted = format_duration(duration_seconds)
        aspect_ratio = calculate_aspect_ratio(width, height)

        metadata = VideoMetadata(
            filename=path.name,
            file_size_bytes=file_size_bytes,
            file_size_mb=file_size_mb,
            width=width,
            height=height,
            fps=round(fps, 2),
            total_frames=total_frames,
            duration_seconds=round(duration_seconds, 2),
            duration_formatted=duration_formatted,
            aspect_ratio=aspect_ratio,
            fourcc_codec=fourcc,
        )

        logger.info(
            "Video metadata parsed successfully: %dx%d @ %.2f fps, %s, %s",
            width,
            height,
            fps,
            duration_formatted,
            fourcc,
        )
        return metadata

    finally:
        cap.release()
