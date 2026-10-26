"""Unit tests for AI Video Copilot chatbot answering engine."""

from pathlib import Path
import pytest

from clipmind.analysis.chatbot import answer_video_query
from clipmind.analysis.description import generate_full_video_narrative
from clipmind.analysis.summary import generate_video_summary
from clipmind.video.detector import VideoSceneDetector
from clipmind.video.keyframe import KeyframeExtractor
from clipmind.video.metadata import extract_video_metadata


def test_chatbot_answering_various_queries(synthetic_multiscene_video: Path, tmp_path: Path):
    """Verify chatbot responds intelligently to various question categories."""
    meta = extract_video_metadata(synthetic_multiscene_video)
    detector = VideoSceneDetector(speed_profile="turbo")
    scenes = detector.detect_scenes(synthetic_multiscene_video, metadata=meta)

    extractor = KeyframeExtractor()
    keyframes = extractor.extract_keyframes(
        video_path=synthetic_multiscene_video,
        scenes=scenes,
        output_dir=tmp_path / "kfs",
    )

    summary = generate_video_summary(meta, scenes, keyframes)
    narrative = generate_full_video_narrative(meta, scenes, keyframes)

    # 1. Social query
    res_social = answer_video_query("How can I make a TikTok or Reel hook from this?", meta, scenes, summary, narrative)
    assert "Social Media & Short-Form Content Strategy" in res_social
    assert "Hook" in res_social

    # 2. Motion query
    res_motion = answer_video_query("What is the motion energy score?", meta, scenes, summary, narrative)
    assert "Motion Dynamics Analysis" in res_motion

    # 3. Color query
    res_color = answer_video_query("Tell me about the color palette and lighting", meta, scenes, summary, narrative)
    assert "Color Grading & Visual Atmosphere" in res_color

    # 4. Music BPM query
    res_music = answer_video_query("Recommend background music and tempo BPM", meta, scenes, summary, narrative)
    assert "BPM" in res_music

    # 5. Scene cuts query
    res_cuts = answer_video_query("List all scene timestamps and cuts", meta, scenes, summary, narrative)
    assert "Scene Cut Breakdown" in res_cuts

    # 6. Specs query
    res_specs = answer_video_query("What are the technical specs?", meta, scenes, summary, narrative)
    assert "Resolution" in res_specs
