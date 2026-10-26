"""Unit tests for keyframe extraction, deduplication, and contact sheet generation."""

from pathlib import Path
import pytest
from PIL import Image

from clipmind.video.detector import VideoSceneDetector
from clipmind.video.keyframe import KeyframeExtractor, generate_contact_sheet


def test_keyframe_extraction_and_contact_sheet(synthetic_multiscene_video: Path, tmp_path: Path):
    """Verify end-to-end keyframe extraction and visual contact sheet generation."""
    detector = VideoSceneDetector(threshold=20.0, min_scene_len_frames=10)
    scenes = detector.detect_scenes(synthetic_multiscene_video)

    output_dir = tmp_path / "keyframes"
    extractor = KeyframeExtractor(strategy="middle", enable_deduplication=True)
    keyframes = extractor.extract_keyframes(
        video_path=synthetic_multiscene_video,
        scenes=scenes,
        output_dir=output_dir,
    )

    assert len(keyframes) == len(scenes)
    for kf in keyframes:
        assert kf.image_path.exists()
        assert kf.width == 320
        assert kf.height == 240
        assert kf.timestamp_seconds >= 0.0

    # Test contact sheet generation
    sheet_path = tmp_path / "contact_sheet.jpg"
    res = generate_contact_sheet(keyframes, sheet_path, columns=2)
    assert res is not None
    assert sheet_path.exists()

    with Image.open(sheet_path) as img:
        assert img.width > 300
        assert img.height > 100


def test_keyframe_extraction_empty_scenes(synthetic_multiscene_video: Path, tmp_path: Path):
    """Verify graceful handling when scene list is empty."""
    extractor = KeyframeExtractor()
    keyframes = extractor.extract_keyframes(
        video_path=synthetic_multiscene_video,
        scenes=[],
        output_dir=tmp_path / "empty",
    )
    assert keyframes == []
