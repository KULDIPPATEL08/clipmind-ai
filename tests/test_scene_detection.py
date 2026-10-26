"""Unit tests for scene boundary detection and timestamp calculation."""

from pathlib import Path
import pytest

from clipmind.video.detector import VideoSceneDetector, seconds_to_timecode


def test_seconds_to_timecode():
    """Verify precision timecode formatting."""
    assert seconds_to_timecode(0.0) == "00:00:00.000"
    assert seconds_to_timecode(65.5) == "00:01:05.500"
    assert seconds_to_timecode(3661.123) == "01:01:01.123"


def test_detect_scenes_multiscene(synthetic_multiscene_video: Path):
    """Verify detection of distinct color scenes in synthetic video."""
    detector = VideoSceneDetector(detector_type="content", threshold=20.0, min_scene_len_frames=10)
    scenes = detector.detect_scenes(synthetic_multiscene_video)

    assert len(scenes) >= 2
    # Verify chronological sequence
    for i in range(len(scenes) - 1):
        assert scenes[i].scene_number == i + 1
        assert scenes[i].start_frame < scenes[i].end_frame
        assert scenes[i].end_time_seconds <= scenes[i + 1].start_time_seconds + 0.1
        assert scenes[i].duration_seconds > 0


def test_detect_scenes_single_scene(synthetic_single_scene_video: Path):
    """Verify single scene video returns exactly one scene."""
    detector = VideoSceneDetector(detector_type="content", threshold=30.0, min_scene_len_frames=10)
    scenes = detector.detect_scenes(synthetic_single_scene_video)

    assert len(scenes) == 1
    assert scenes[0].scene_number == 1
    assert scenes[0].start_frame == 0


def test_detect_scenes_opencv_fallback(synthetic_multiscene_video: Path):
    """Verify the OpenCV histogram differencing fallback directly."""
    from clipmind.video.metadata import extract_video_metadata
    meta = extract_video_metadata(synthetic_multiscene_video)
    detector = VideoSceneDetector(threshold=20.0, min_scene_len_frames=5)
    scenes = detector._detect_with_opencv_fallback(synthetic_multiscene_video, meta)
    assert len(scenes) >= 2
    for s in scenes:
        assert s.duration_seconds > 0
