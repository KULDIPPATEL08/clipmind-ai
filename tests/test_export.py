"""Unit tests for ZIP packaging, CSV tables, JSON metadata, and Markdown reports."""

import json
import zipfile
from pathlib import Path
import pytest

from clipmind.analysis.summary import generate_video_summary
from clipmind.export.exporter import (
    create_keyframe_zip,
    export_scenes_csv,
    export_summary_json,
    export_summary_markdown,
)
from clipmind.video.detector import VideoSceneDetector
from clipmind.video.keyframe import KeyframeExtractor
from clipmind.video.metadata import extract_video_metadata


def test_complete_export_workflow(synthetic_multiscene_video: Path, tmp_path: Path):
    """Verify all export formats produce valid, readable files."""
    metadata = extract_video_metadata(synthetic_multiscene_video)
    detector = VideoSceneDetector(threshold=20.0, min_scene_len_frames=10)
    scenes = detector.detect_scenes(synthetic_multiscene_video, metadata=metadata)

    extractor = KeyframeExtractor()
    keyframes = extractor.extract_keyframes(
        video_path=synthetic_multiscene_video,
        scenes=scenes,
        output_dir=tmp_path / "kf",
    )
    summary = generate_video_summary(metadata, scenes, keyframes)

    export_dir = tmp_path / "exports"

    # 1. ZIP Archive
    zip_path = export_dir / "keyframes.zip"
    create_keyframe_zip(keyframes, zip_path)
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        assert len(namelist) == len(keyframes)
        assert all(n.endswith(".jpg") for n in namelist)

    # 2. CSV
    csv_path = export_dir / "scenes.csv"
    export_scenes_csv(scenes, csv_path)
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "scene_number" in content
    assert "start_timecode" in content

    # 3. JSON
    json_path = export_dir / "report.json"
    export_summary_json(metadata, summary, scenes, json_path)
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert "metadata" in data
    assert "summary" in data
    assert "scenes" in data
    assert data["metadata"]["width"] == 320

    # 4. Markdown Report
    md_path = export_dir / "report.md"
    export_summary_markdown(metadata, summary, scenes, md_path)
    assert md_path.exists()
    md_text = md_path.read_text(encoding="utf-8")
    assert "# ClipMind AI" in md_text
    assert "Scene Index Table" in md_text
