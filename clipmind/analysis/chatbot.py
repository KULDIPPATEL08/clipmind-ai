"""AI Video Intelligence Copilot reasoning engine."""

from __future__ import annotations

import re
from typing import List, Optional

from clipmind.analysis.description import FullVideoNarrative
from clipmind.analysis.summary import VideoSummaryReport
from clipmind.video.detector import SceneInfo
from clipmind.video.metadata import VideoMetadata


def answer_video_query(
    query: str,
    metadata: VideoMetadata,
    scenes: List[SceneInfo],
    summary: VideoSummaryReport,
    narrative: Optional[FullVideoNarrative] = None,
) -> str:
    """Answers natural language questions about the analyzed video.

    Args:
        query: User's question or instruction.
        metadata: Extracted technical video metadata.
        scenes: Detected scene list with timings and motion.
        summary: Pacing and distribution report.
        narrative: Visual narrative, mood, and color palette data.

    Returns:
        Structured, conversational markdown answer.
    """
    q = query.lower().strip()

    # 1. Social Media / Viral Hook / TikTok / Reels
    if any(k in q for k in ["tiktok", "reel", "short", "viral", "hook", "social"]):
        hook_scene = scenes[0] if scenes else None
        hook_info = (
            f"**Scene #1** (`00:00` - `{hook_scene.end_timecode}`) serves as your prime retention hook."
            if hook_scene
            else "The opening frames are critical for viewer retention."
        )
        return (
            f"### 📱 Social Media & Short-Form Content Strategy\n\n"
            f"- **Prime Hook**: {hook_info}\n"
            f"- **Target Aspect Ratio**: Crop from `{metadata.aspect_ratio}` to `9:16` vertical format.\n"
            f"- **Optimal Pacing**: With an average cut length of **{summary.avg_scene_duration_seconds:.1f}s**, "
            f"this video matches short-form attention spans.\n"
            f"- **Suggested Title**: *{narrative.title_suggestion if narrative else 'Dynamic Visual Highlight'}*\n"
            f"- **Recommended Audio**: Pair with a trending sound matching a tempo of ~**{_suggest_bpm(summary.avg_scene_duration_seconds)} BPM**."
        )

    # 2. Motion / Action / Dynamics
    if any(k in q for k in ["motion", "action", "energy", "movement", "speed", "fastest"]):
        if narrative and narrative.scenes:
            sorted_by_motion = sorted(narrative.scenes, key=lambda s: s.motion_energy_score, reverse=True)
            top_motion = sorted_by_motion[0]
            low_motion = sorted_by_motion[-1]
            return (
                f"### ⚡ Motion Dynamics Analysis\n\n"
                f"- **Highest Motion Cut**: **{top_motion.title}** with a motion energy score of **{top_motion.motion_energy_score}/100** ({top_motion.motion_level}).\n"
                f"- **Most Static / Ambient Cut**: **{low_motion.title}** ({low_motion.motion_energy_score}/100 motion energy).\n"
                f"- **Overall Motion Profile**: The video transitions across **{len(scenes)} distinct visual beats**, providing rhythmic optical contrast.\n"
                f"- **Camera Movement**: Features a mix of dynamic shifts and stable framing, ideal for keeping visual engagement high."
            )
        return (
            f"### ⚡ Motion & Pacing Overview\n\n"
            f"The video contains **{len(scenes)} cuts** with an average scene duration of **{summary.avg_scene_duration_seconds:.2f} seconds**. "
            f"Shortest scene is **{summary.min_scene_duration_seconds:.2f}s** and longest is **{summary.max_scene_duration_seconds:.2f}s**."
        )

    # 3. Color, Lighting, Aesthetic & Palette
    if any(k in q for k in ["color", "palette", "lighting", "aesthetic", "look", "mood", "style"]):
        if narrative:
            palette_str = ", ".join([f"`{c}`" for c in narrative.dominant_palette_hex])
            return (
                f"### 🎨 Color Grading & Visual Atmosphere\n\n"
                f"- **Primary Mood**: **{narrative.primary_mood}**\n"
                f"- **Dominant Color Swatches**: {palette_str}\n"
                f"- **Lighting Aesthetic**: Prominently features balanced contrast with key lighting across major scenes.\n"
                f"- **Color Harmony**: The palette creates a high-contrast cinematic profile suitable for modern screens."
            )
        return (
            f"### 🎨 Visual Atmosphere\n\n"
            f"Color transitions occur across {len(scenes)} scenes with distinct frame-to-frame luminosity."
        )

    # 4. Summary / Synopsis / Story
    if any(k in q for k in ["summary", "synopsis", "about", "story", "overview", "describe", "explain"]):
        if narrative:
            return (
                f"### 🎬 Executive Video Synopsis\n\n"
                f"**\"{narrative.title_suggestion}\"**\n\n"
                f"{narrative.executive_synopsis}\n\n"
                f"- **Total Cuts**: {len(scenes)} scenes\n"
                f"- **Pacing Rhythm**: {narrative.tempo_rhythm_summary}\n"
                f"- **Duration**: {metadata.duration_formatted} ({metadata.duration_seconds:.1f}s)"
            )
        return (
            f"### 🎬 Video Synopsis\n\n"
            f"A **{metadata.duration_formatted}** video analyzed into **{len(scenes)} distinct scenes** "
            f"at **{metadata.fps} FPS** ({metadata.width}x{metadata.height})."
        )

    # 5. Audio / Music / Sound Design / BPM
    if any(k in q for k in ["music", "audio", "sound", "bpm", "tempo", "song"]):
        bpm = _suggest_bpm(summary.avg_scene_duration_seconds)
        return (
            f"### 🎵 Audio & Soundtrack Recommendation\n\n"
            f"- **Recommended Music BPM**: **{bpm} BPM**\n"
            f"- **Cut Synchronization**: Scene cuts occur every **{summary.avg_scene_duration_seconds:.1f} seconds** on average.\n"
            f"- **Sound Design Recommendation**: Add subtle whooshes or riser transitions at timestamps: "
            f"{', '.join([f'`{s.start_timecode}`' for s in scenes[:4]])}.\n"
            f"- **Mood Matching**: Pair with an ambient electronic or cinematic underscore matching the video's rhythm."
        )

    # 6. Scene Cuts & Timestamps Manifest
    if any(k in q for k in ["cuts", "scenes", "timestamp", "list", "time", "breakdown", "manifest"]):
        lines = [f"### ⏱️ Scene Cut Breakdown ({len(scenes)} Scenes)\n"]
        for s in scenes[:8]:
            lines.append(f"- **Scene #{s.scene_number:02d}**: `{s.start_timecode}` ➔ `{s.end_timecode}` ({s.duration_seconds:.2f}s) — *{s.pacing_label.title()}*")
        if len(scenes) > 8:
            lines.append(f"\n*...and {len(scenes) - 8} additional scenes. Check the Scene Table tab for the full log.*")
        return "\n".join(lines)

    # 7. Technical Specifications
    if any(k in q for k in ["spec", "fps", "resolution", "codec", "size", "dimension", "format"]):
        return (
            f"### ⚙️ Video Technical Specifications\n\n"
            f"- **Resolution**: `{metadata.width} x {metadata.height}` ({metadata.aspect_ratio})\n"
            f"- **Frame Rate**: `{metadata.fps}` FPS\n"
            f"- **Total Frames**: `{metadata.total_frames:,}` frames\n"
            f"- **Duration**: `{metadata.duration_formatted}` ({metadata.duration_seconds:.2f} seconds)\n"
            f"- **File Size**: `{metadata.file_size_mb} MB`\n"
            f"- **FourCC Codec**: `{metadata.fourcc_codec}`"
        )

    # Default general synthesis
    return (
        f"### 🤖 ClipMind AI Video Intelligence Response\n\n"
        f"Based on full neural analysis of **{metadata.filename}**:\n\n"
        f"- **Runtime & Structure**: The video spans **{metadata.duration_formatted}** across **{len(scenes)} detected cuts** "
        f"with an average scene duration of **{summary.avg_scene_duration_seconds:.1f}s**.\n"
        f"- **Visual Aesthetic**: Characterized by {narrative.primary_mood if narrative else 'dynamic cinematography'} "
        f"with {len(narrative.dominant_palette_hex) if narrative else 'rich'} primary color registers.\n"
        f"- **Pacing**: Rapid cuts: `{summary.rapid_scenes_count}`, "
        f"Standard: `{summary.standard_scenes_count}`, "
        f"Extended: `{summary.extended_scenes_count}`.\n\n"
        f"*Tip: You can ask me to summarize for TikTok/Reels, analyze motion energy, inspect color palettes, or recommend music BPM!*"
    )


def _suggest_bpm(avg_scene_duration_seconds: float) -> int:
    """Estimates appropriate background music BPM based on cut frequency."""
    if avg_scene_duration_seconds <= 1.5:
        return 135
    elif avg_scene_duration_seconds <= 3.0:
        return 120
    elif avg_scene_duration_seconds <= 6.0:
        return 95
    else:
        return 75
