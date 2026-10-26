"""Pytest fixtures and synthetic video generators for automated testing."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Generator

import cv2
import numpy as np
import pytest

from clipmind.config import AppConfig


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Provides an isolated temporary workspace directory."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.fixture
def synthetic_multiscene_video(temp_workspace: Path) -> Path:
    """Generates a small 3-scene synthetic MP4 video with hard cuts."""
    video_path = temp_workspace / "multiscene.mp4"
    width, height, fps = 320, 240, 24
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

    # 3 distinct colors representing 3 scenes, 24 frames (~1 sec) each
    scene_colors = [
        (0, 0, 255),    # Red (BGR)
        (0, 255, 0),    # Green (BGR)
        (255, 0, 0),    # Blue (BGR)
    ]

    for bgr in scene_colors:
        for _ in range(24):
            frame = np.full((height, width, 3), bgr, dtype=np.uint8)
            writer.write(frame)

    writer.release()
    return video_path


@pytest.fixture
def synthetic_single_scene_video(temp_workspace: Path) -> Path:
    """Generates a single continuous steady video."""
    video_path = temp_workspace / "single_scene.mp4"
    width, height, fps = 320, 240, 24
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

    frame = np.full((height, width, 3), (120, 120, 120), dtype=np.uint8)
    for _ in range(30):
        writer.write(frame)

    writer.release()
    return video_path


@pytest.fixture
def corrupted_video_file(temp_workspace: Path) -> Path:
    """Creates a corrupted file with fake MP4 extension."""
    corrupted_path = temp_workspace / "corrupted.mp4"
    # Write garbage random bytes
    corrupted_path.write_bytes(b"\x00\x01\x02CORRUPTED_VIDEO_BYTES_NOT_VALID")
    return corrupted_path


@pytest.fixture
def valid_mp4_bytes(synthetic_multiscene_video: Path) -> bytes:
    """Returns raw bytes of a valid MP4 file."""
    return synthetic_multiscene_video.read_bytes()
