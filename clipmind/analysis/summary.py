"""Video scene metrics, pacing analysis, and visual summary generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from clipmind.video.detector import SceneInfo
from clipmind.video.keyframe import Keyframe
from clipmind.video.metadata import VideoMetadata, format_duration


@dataclass
class VideoSummaryReport:
    """Consolidated analytical summary of the analyzed video."""

    total_scenes: int
    total_duration_seconds: float
    total_duration_formatted: str
    avg_scene_duration_seconds: float
    avg_scene_duration_formatted: str
    min_scene_duration_seconds: float
    max_scene_duration_seconds: float
    scenes_per_minute: float
    rapid_scenes_count: int
    rapid_scenes_pct: float
    standard_scenes_count: int
    standard_scenes_pct: float
    extended_scenes_count: int
    extended_scenes_pct: float
    extracted_keyframes_count: int
    unique_keyframes_count: int
    narrative_breakdown: List[Dict[str, Any]]
    methodology_note: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(self)


def generate_video_summary(
    metadata: VideoMetadata,
    scenes: List[SceneInfo],
    keyframes: List[Keyframe],
) -> VideoSummaryReport:
    """Computes comprehensive visual pacing analytics and structured scene summary.

    Note: This summary is based on deterministic computer vision (scene cut detection,
    frame color histogram diffs, and duration pacing), avoiding generative hallucinations.
    """
    total_scenes = len(scenes)
    total_duration = max(0.01, metadata.duration_seconds)
    extracted_count = len(keyframes)
    unique_count = sum(1 for k in keyframes if not k.is_duplicate)

    if total_scenes == 0:
        return VideoSummaryReport(
            total_scenes=0,
            total_duration_seconds=total_duration,
            total_duration_formatted=metadata.duration_formatted,
            avg_scene_duration_seconds=0.0,
            avg_scene_duration_formatted="00:00",
            min_scene_duration_seconds=0.0,
            max_scene_duration_seconds=0.0,
            scenes_per_minute=0.0,
            rapid_scenes_count=0,
            rapid_scenes_pct=0.0,
            standard_scenes_count=0,
            standard_scenes_pct=0.0,
            extended_scenes_count=0,
            extended_scenes_pct=0.0,
            extracted_keyframes_count=0,
            unique_keyframes_count=0,
            narrative_breakdown=[],
            methodology_note=(
                "Summary generated via OpenCV/PySceneDetect deterministic computer vision. "
                "No external LLM or deep generative network was invoked."
            ),
        )

    durations = [s.duration_seconds for s in scenes]
    avg_duration = sum(durations) / total_scenes
    min_duration = min(durations)
    max_duration = max(durations)
    spm = round((total_scenes / total_duration) * 60, 2)

    rapid = [d for d in durations if d < 2.0]
    standard = [d for d in durations if 2.0 <= d <= 8.0]
    extended = [d for d in durations if d > 8.0]

    rapid_pct = round((len(rapid) / total_scenes) * 100, 1)
    standard_pct = round((len(standard) / total_scenes) * 100, 1)
    extended_pct = round((len(extended) / total_scenes) * 100, 1)

    # Segment scenes into 3 logical phases: Intro, Body, Conclusion
    breakdown = []
    if total_scenes == 1:
        breakdown.append({
            "phase": "Continuous Shot / Uncut Video",
            "scenes_range": "Scene 1",
            "timecode_range": f"{scenes[0].start_timecode} - {scenes[0].end_timecode}",
            "description": "Entire video comprises a single steady scene without significant cut transitions.",
        })
    else:
        intro_cutoff = max(1, total_scenes // 4)
        outro_cutoff = max(intro_cutoff + 1, total_scenes - max(1, total_scenes // 4))

        breakdown.append({
            "phase": "Opening / Intro Segment",
            "scenes_range": f"Scenes 1 to {intro_cutoff}",
            "timecode_range": f"{scenes[0].start_timecode} - {scenes[intro_cutoff - 1].end_timecode}",
            "description": f"Initial exposition phase encompassing {intro_cutoff} scene(s).",
        })

        if outro_cutoff > intro_cutoff:
            breakdown.append({
                "phase": "Core Sequence / Main Body",
                "scenes_range": f"Scenes {intro_cutoff + 1} to {outro_cutoff}",
                "timecode_range": f"{scenes[intro_cutoff].start_timecode} - {scenes[outro_cutoff - 1].end_timecode}",
                "description": f"Central action/narrative phase spanning {outro_cutoff - intro_cutoff} scene transitions.",
            })

        breakdown.append({
            "phase": "Closing / Outro Segment",
            "scenes_range": f"Scenes {outro_cutoff + 1} to {total_scenes}",
            "timecode_range": f"{scenes[outro_cutoff].start_timecode} - {scenes[-1].end_timecode}",
            "description": f"Concluding sequence with {total_scenes - outro_cutoff} scene(s).",
        })

    methodology = (
        "Summary and keyframe distribution are computed using algorithmic scene boundary detection "
        "(PySceneDetect / OpenCV frame correlation) and color histogram deduplication. "
        "This provides an objective, transparent visual breakdown of the video structure without generative hallucinations."
    )

    return VideoSummaryReport(
        total_scenes=total_scenes,
        total_duration_seconds=round(total_duration, 2),
        total_duration_formatted=metadata.duration_formatted,
        avg_scene_duration_seconds=round(avg_duration, 2),
        avg_scene_duration_formatted=format_duration(avg_duration),
        min_scene_duration_seconds=round(min_duration, 2),
        max_scene_duration_seconds=round(max_duration, 2),
        scenes_per_minute=spm,
        rapid_scenes_count=len(rapid),
        rapid_scenes_pct=rapid_pct,
        standard_scenes_count=len(standard),
        standard_scenes_pct=standard_pct,
        extended_scenes_count=len(extended),
        extended_scenes_pct=extended_pct,
        extracted_keyframes_count=extracted_count,
        unique_keyframes_count=unique_count,
        narrative_breakdown=breakdown,
        methodology_note=methodology,
    )
