"""Deep visual analysis and narrative video description engine."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from clipmind.logger import logger
from clipmind.video.detector import SceneInfo
from clipmind.video.keyframe import Keyframe
from clipmind.video.metadata import VideoMetadata, format_duration


@dataclass
class SceneDescription:
    """Rich visual and narrative description for an individual video scene."""

    scene_number: int
    title: str
    timecode_range: str
    duration_str: str
    summary_narrative: str
    dominant_hex_colors: List[str]
    mood_tag: str
    motion_energy_score: int  # 0 to 100
    motion_level: str  # "Low / Static", "Moderate Pacing", "High Action"
    shot_type_estimate: str  # "Panoramic / Wide", "Medium Shot", "Close-up / High-Focus"
    lighting_key: str  # "High-Key Vivid", "Balanced Exposure", "Low-Key Moody"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FullVideoNarrative:
    """Comprehensive, executive-level video description and aesthetic analysis."""

    title_suggestion: str
    executive_synopsis: str
    visual_atmosphere: str
    primary_mood: str
    dominant_palette_hex: List[str]
    tempo_rhythm_summary: str
    total_scenes_count: int
    scenes: List[SceneDescription]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def extract_dominant_colors(image_path: Path, n_colors: int = 3) -> List[str]:
    """Extracts top dominant color hex codes using fast k-means clustering."""
    try:
        path = str(image_path)
        img = cv2.imread(path)
        if img is None:
            return ["#2563eb", "#10b981", "#f59e0b"]

        # Downsample for microsecond execution
        small = cv2.resize(img, (80, 45), interpolation=cv2.INTER_AREA)
        pixels = np.float32(small.reshape(-1, 3))

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        k = max(1, min(n_colors, len(pixels)))
        _, _, centers = cv2.kmeans(pixels, k, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)

        hex_colors = []
        for c in centers:
            b, g, r = int(np.clip(c[0], 0, 255)), int(np.clip(c[1], 0, 255)), int(np.clip(c[2], 0, 255))
            hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")

        return hex_colors or ["#3b82f6"]
    except Exception as e:
        logger.debug("Dominant color extraction fallback: %s", e)
        return ["#2563eb", "#4f46e5", "#06b6d4"]


def analyze_scene_visuals(
    keyframe_path: Path,
    duration: float,
) -> Tuple[int, str, str, str]:
    """Analyzes lighting, contrast, and motion energy proxy from keyframe metrics."""
    try:
        img = cv2.imread(str(keyframe_path))
        if img is None:
            return 50, "Moderate Pacing", "Medium Shot", "Balanced Exposure"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))

        # Lighting key classification
        if brightness > 165:
            lighting = "High-Key Vivid"
        elif brightness < 60:
            lighting = "Low-Key Moody"
        else:
            lighting = "Balanced Exposure"

        # Shot complexity / detail classification based on Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var > 400:
            shot_type = "Close-up / High-Focus"
        elif laplacian_var < 90:
            shot_type = "Panoramic / Wide"
        else:
            shot_type = "Medium Shot"

        # Motion score estimate combining cut pacing and spatial edge energy
        if duration < 2.0:
            motion_score = min(98, int(75 + (contrast / 255.0) * 20))
            motion_level = "High Action"
        elif duration > 8.0:
            motion_score = max(12, int(25 + (contrast / 255.0) * 15))
            motion_level = "Low / Static"
        else:
            motion_score = int(45 + (contrast / 255.0) * 25)
            motion_level = "Moderate Pacing"

        return motion_score, motion_level, shot_type, lighting

    except Exception:
        return 50, "Moderate Pacing", "Medium Shot", "Balanced Exposure"


def generate_full_video_narrative(
    metadata: VideoMetadata,
    scenes: List[SceneInfo],
    keyframes: List[Keyframe],
) -> FullVideoNarrative:
    """Generates an executive-level, narrative description of the video and its constituent scenes."""
    if not scenes:
        return FullVideoNarrative(
            title_suggestion=f"Visual Overview: {metadata.filename}",
            executive_synopsis="No scenes detected in the video stream.",
            visual_atmosphere="Standard",
            primary_mood="Neutral",
            dominant_palette_hex=["#2563eb"],
            tempo_rhythm_summary="Continuous single sequence.",
            total_scenes_count=0,
            scenes=[],
        )

    # Keyframe mapping
    kf_map: Dict[int, Keyframe] = {k.scene_number: k for k in keyframes}
    scene_descriptions: List[SceneDescription] = []
    all_colors: List[str] = []
    total_motion = 0

    mood_keywords = [
        "Vibrant & Dynamic",
        "Cinematic & Structured",
        "Fast-Paced Montage",
        "Atmospheric & Serene",
        "High-Energy Presentation",
    ]

    for s in scenes:
        kf = kf_map.get(s.scene_number)
        colors = ["#2563eb", "#3b82f6"]
        motion_score, motion_level, shot_type, lighting = 50, "Moderate Pacing", "Medium Shot", "Balanced Exposure"

        if kf and kf.image_path.exists():
            colors = extract_dominant_colors(kf.image_path, n_colors=3)
            all_colors.extend(colors)
            motion_score, motion_level, shot_type, lighting = analyze_scene_visuals(
                kf.image_path, s.duration_seconds
            )

        total_motion += motion_score

        # Color mood naming heuristic
        first_hex = colors[0].lower() if colors else "#3b82f6"
        if "#ff" in first_hex or "#ee" in first_hex or "#c" in first_hex[:3]:
            mood_tag = "Warm & Energetic"
        elif "#0" in first_hex[:3] or "#1" in first_hex[:3] or "#2" in first_hex[:3]:
            mood_tag = "Cool & Cinematic"
        else:
            mood_tag = "Natural & Balanced"

        # Generate descriptive title and narrative
        if s.scene_number == 1:
            title = f"Scene 01: Opening Exposition ({s.start_timecode} - {s.end_timecode})"
            narrative = (
                f"The video opens with an establishing sequence lasting {s.duration_seconds:.2f} seconds. "
                f"Features a {shot_type.lower()} under {lighting.lower()} lighting, establishing the initial visual theme."
            )
        elif s.scene_number == len(scenes):
            title = f"Scene {s.scene_number:02d}: Concluding Outro ({s.start_timecode} - {s.end_timecode})"
            narrative = (
                f"The concluding act spans {s.duration_seconds:.2f} seconds with {motion_level.lower()} motion. "
                f"Rounds off the narrative progression with {lighting.lower()} lighting cues."
            )
        else:
            title = f"Scene {s.scene_number:02d}: Progressive Cut ({s.start_timecode} - {s.end_timecode})"
            narrative = (
                f"Intermediate transition sequence lasting {s.duration_seconds:.2f}s with an activity score of {motion_score}/100. "
                f"Shot style reflects {shot_type.lower()} with dominant color accents ({', '.join(colors[:2])})."
            )

        scene_descriptions.append(
            SceneDescription(
                scene_number=s.scene_number,
                title=title,
                timecode_range=f"{s.start_timecode} - {s.end_timecode}",
                duration_str=f"{s.duration_seconds:.2f}s",
                summary_narrative=narrative,
                dominant_hex_colors=colors,
                mood_tag=mood_tag,
                motion_energy_score=motion_score,
                motion_level=motion_level,
                shot_type_estimate=shot_type,
                lighting_key=lighting,
            )
        )

    # Executive Overview
    avg_motion = int(total_motion / max(1, len(scenes)))
    cuts_per_min = (len(scenes) / max(0.01, metadata.duration_seconds)) * 60

    if cuts_per_min > 25:
        rhythm = f"Rapid-Fire Dynamic Montage ({cuts_per_min:.1f} cuts/min)"
        primary_mood = "High-Energy Action"
    elif cuts_per_min < 8:
        rhythm = f"Slow Cinematic Cadence ({cuts_per_min:.1f} cuts/min)"
        primary_mood = "Atmospheric & Narrative"
    else:
        rhythm = f"Standard Commercial / Editorial Cadence ({cuts_per_min:.1f} cuts/min)"
        primary_mood = "Engaging & Structured"

    top_palette = list(dict.fromkeys(all_colors))[:5] or ["#2563eb", "#10b981", "#f59e0b"]

    synopsis = (
        f"This video production contains {len(scenes)} distinct scene cuts across a total runtime of "
        f"{metadata.duration_formatted} ({metadata.duration_seconds:.1f}s) at {metadata.width}x{metadata.height} resolution ({metadata.fps} fps). "
        f"The visual progression is characterized by a {rhythm.lower()} with an average scene duration of "
        f"{metadata.duration_seconds / max(1, len(scenes)):.1f}s. "
        f"Aesthetic lighting maintains predominantly {scene_descriptions[0].lighting_key.lower()} styling, "
        f"with a collective motion energy rating of {avg_motion}/100."
    )

    clean_name = Path(metadata.filename).stem.replace("_", " ").title()
    title_suggestion = f"ClipMind Intelligence Report — {clean_name}"

    return FullVideoNarrative(
        title_suggestion=title_suggestion,
        executive_synopsis=synopsis,
        visual_atmosphere=f"Multi-tonal {primary_mood.lower()} with {len(scenes)} thematic transitions.",
        primary_mood=primary_mood,
        dominant_palette_hex=top_palette,
        tempo_rhythm_summary=rhythm,
        total_scenes_count=len(scenes),
        scenes=scene_descriptions,
    )
