"""Unit tests for video clipping engine and clip packaging."""

from pathlib import Path
import pytest
import cv2

from clipmind.export.exporter import create_video_clips_zip
from clipmind.video.clipper import extract_scene_clips
from clipmind.video.detector import VideoSceneDetector


def test_extract_scene_clips_and_zip(synthetic_multiscene_video: Path, tmp_path: Path):
    """Verify extracting frame-accurate video clips for detected scenes."""
    detector = VideoSceneDetector(detector_type="hybrid", threshold=20.0, min_scene_len_frames=10)
    scenes = detector.detect_scenes(synthetic_multiscene_video)
    assert len(scenes) >= 2

    clips_dir = tmp_path / "clips"
    extracted_clips = extract_scene_clips(
        video_path=synthetic_multiscene_video,
        scenes=scenes,
        output_dir=clips_dir,
    )

    assert len(extracted_clips) == len(scenes)
    for clip_path in extracted_clips:
        assert clip_path.exists()
        assert clip_path.stat().st_size > 0
        assert clip_path.suffix == ".mp4"

        # Verify that OpenCV can open and decode the generated video clip
        cap = cv2.VideoCapture(str(clip_path))
        assert cap.isOpened()
        ret, frame = cap.read()
        assert ret is True
        assert frame is not None
        cap.release()

    # Verify that each scene has clip metadata populated
    for s in scenes:
        assert s.clip_path is not None
        assert s.clip_filename is not None
        assert s.clip_size_mb is not None

    # Test packaging into video clips ZIP
    zip_path = tmp_path / "scene_clips.zip"
    res_zip = create_video_clips_zip(scenes, zip_path)
    assert res_zip.exists()
    assert res_zip.stat().st_size > 0


def test_extract_scene_clips_empty_scenes(synthetic_multiscene_video: Path, tmp_path: Path):
    """Verify handling when scenes list is empty."""
    clips = extract_scene_clips(
        video_path=synthetic_multiscene_video,
        scenes=[],
        output_dir=tmp_path / "empty_clips",
    )
    assert clips == []
