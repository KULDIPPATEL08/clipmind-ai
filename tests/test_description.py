"""Unit tests for deep video narrative and scene description engine."""

from pathlib import Path
import pytest
from PIL import Image

from clipmind.analysis.description import (
    analyze_scene_visuals,
    extract_dominant_colors,
    generate_full_video_narrative,
)
from clipmind.video.detector import VideoSceneDetector
from clipmind.video.keyframe import KeyframeExtractor
from clipmind.video.metadata import extract_video_metadata


def test_extract_dominant_colors(tmp_path: Path):
    """Verify dominant color hex extraction from an image."""
    img_path = tmp_path / "test_color.jpg"
    img = Image.new("RGB", (60, 60), color=(255, 0, 0))  # Red
    img.save(img_path)

    hex_colors = extract_dominant_colors(img_path, n_colors=2)
    assert len(hex_colors) >= 1
    assert any(h.startswith("#") for h in hex_colors)


def test_analyze_scene_visuals(tmp_path: Path):
    """Verify lighting, shot type, and motion analysis proxies."""
    img_path = tmp_path / "test_visuals.jpg"
    img = Image.new("RGB", (100, 100), color=(200, 200, 200))
    img.save(img_path)

    motion_score, motion_level, shot_type, lighting = analyze_scene_visuals(img_path, duration=1.5)
    assert 0 <= motion_score <= 100
    assert motion_level in ["Low / Static", "Moderate Pacing", "High Action"]
    assert len(shot_type) > 0
    assert len(lighting) > 0


def test_generate_full_video_narrative(synthetic_multiscene_video: Path, tmp_path: Path):
    """Verify end-to-end full video synopsis and scene description synthesis."""
    meta = extract_video_metadata(synthetic_multiscene_video)
    detector = VideoSceneDetector(speed_profile="fast")
    scenes = detector.detect_scenes(synthetic_multiscene_video, metadata=meta)

    extractor = KeyframeExtractor()
    keyframes = extractor.extract_keyframes(
        video_path=synthetic_multiscene_video,
        scenes=scenes,
        output_dir=tmp_path / "kfs",
    )

    narrative = generate_full_video_narrative(meta, scenes, keyframes)
    assert narrative.title_suggestion.startswith("ClipMind Intelligence Report")
    assert len(narrative.executive_synopsis) > 20
    assert len(narrative.dominant_palette_hex) >= 1
    assert len(narrative.scenes) == len(scenes)

    for s in narrative.scenes:
        assert len(s.title) > 0
        assert len(s.summary_narrative) > 0
        assert len(s.dominant_hex_colors) >= 1
        assert 0 <= s.motion_energy_score <= 100


def test_generate_narrative_empty_scenes(synthetic_multiscene_video: Path):
    """Verify graceful handling when no scenes are present."""
    meta = extract_video_metadata(synthetic_multiscene_video)
    narrative = generate_full_video_narrative(meta, [], [])
    assert narrative.total_scenes_count == 0
    assert len(narrative.scenes) == 0
