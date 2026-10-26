"""Unit tests for video metadata extraction and decodability validation."""

from pathlib import Path
import pytest

from clipmind.exceptions import CorruptedVideoError, SecurityValidationError
from clipmind.video.metadata import (
    calculate_aspect_ratio,
    extract_video_metadata,
    format_duration,
)


def test_format_duration():
    """Verify time formatting logic."""
    assert format_duration(45.2) == "00:45"
    assert format_duration(125.0) == "02:05"
    assert format_duration(3665.0) == "01:01:05"
    assert format_duration(0.0) == "00:00"


def test_calculate_aspect_ratio():
    """Verify standard aspect ratio identification."""
    assert "16:9" in calculate_aspect_ratio(1920, 1080)
    assert "16:9" in calculate_aspect_ratio(1280, 720)
    assert "4:3" in calculate_aspect_ratio(640, 480)
    assert "1:1" in calculate_aspect_ratio(500, 500)
    assert "9:16" in calculate_aspect_ratio(1080, 1920)


def test_extract_metadata_success(synthetic_multiscene_video: Path):
    """Verify extraction of accurate metadata from valid video."""
    meta = extract_video_metadata(synthetic_multiscene_video)
    assert meta.width == 320
    assert meta.height == 240
    assert meta.fps == 24.0
    assert meta.total_frames >= 70
    assert meta.duration_seconds > 2.0
    assert meta.aspect_ratio == "4:3 (Standard)"
    assert meta.file_size_bytes > 0


def test_extract_metadata_corrupted_file(corrupted_video_file: Path):
    """Verify that attempting to extract metadata from corrupted file raises CorruptedVideoError."""
    with pytest.raises(CorruptedVideoError):
        extract_video_metadata(corrupted_video_file)


def test_extract_metadata_missing_file(tmp_path: Path):
    """Verify error when video path does not exist."""
    non_existent = tmp_path / "does_not_exist.mp4"
    with pytest.raises(CorruptedVideoError):
        extract_video_metadata(non_existent)
