"""Configuration settings for ClipMind AI."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set


@dataclass
class AppConfig:
    """Application configuration with environment variable support."""

    # Application metadata
    app_name: str = "ClipMind AI"
    app_version: str = "1.0.0"
    debug: bool = field(
        default_factory=lambda: os.getenv("CLIPMIND_DEBUG", "false").lower() == "true"
    )

    # Storage and paths
    base_temp_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("CLIPMIND_TEMP_DIR", Path.cwd() / ".clipmind_tmp")
        ).resolve()
    )
    cleanup_on_completion: bool = field(
        default_factory=lambda: os.getenv("CLIPMIND_AUTO_CLEANUP", "true").lower() == "true"
    )

    # Security and Upload limits
    max_upload_size_mb: int = field(
        default_factory=lambda: int(os.getenv("CLIPMIND_MAX_UPLOAD_MB", "500"))
    )
    max_video_duration_seconds: int = field(
        default_factory=lambda: int(os.getenv("CLIPMIND_MAX_DURATION_SEC", "3600"))
    )
    allowed_extensions: Set[str] = field(
        default_factory=lambda: {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    )
    max_frame_dimension: int = field(
        default_factory=lambda: int(os.getenv("CLIPMIND_MAX_FRAME_DIM", "4096"))
    )

    # Scene Detection defaults
    default_detector: str = "content"  # "content", "adaptive", "threshold"
    default_content_threshold: float = 27.0
    default_min_scene_length_frames: int = 15
    max_scenes_limit: int = 500

    # Keyframe Extraction defaults
    default_keyframe_strategy: str = "middle"  # "middle", "start", "peak"
    max_keyframes_limit: int = 200
    enable_deduplication: bool = True
    deduplication_threshold: float = 0.90  # cosine/hist similarity above this is considered duplicate

    # Contact sheet settings
    contact_sheet_columns: int = 4
    contact_sheet_thumb_width: int = 320

    def __post_init__(self) -> None:
        """Validate and prepare configuration paths."""
        self.allowed_extensions = {ext.lower() for ext in self.allowed_extensions}
        self.base_temp_dir.mkdir(parents=True, exist_ok=True)

    @property
    def temp_dir(self) -> Path:
        """Alias for base_temp_dir for convenience."""
        return self.base_temp_dir



# Global default configuration instance
config = AppConfig()
