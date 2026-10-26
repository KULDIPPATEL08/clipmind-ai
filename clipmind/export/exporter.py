"""Export utilities for packaging keyframes, CSV scene manifests, JSON schemas, and reports."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from typing import List, Optional

from clipmind.analysis.summary import VideoSummaryReport
from clipmind.exceptions import ExportError
from clipmind.logger import logger
from clipmind.video.detector import SceneInfo
from clipmind.video.keyframe import Keyframe
from clipmind.video.metadata import VideoMetadata


def create_keyframe_zip(
    keyframes: List[Keyframe],
    output_zip_path: Path,
    include_duplicates: bool = False,
) -> Path:
    """Packages extracted keyframes into a compressed ZIP archive."""
    output_zip_path = Path(output_zip_path).resolve()
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)

    valid_frames = [
        k for k in keyframes if k.image_path.exists() and (include_duplicates or not k.is_duplicate)
    ]
    if not valid_frames:
        raise ExportError(
            "No valid keyframe images found to package into ZIP archive.",
            user_friendly_message="No keyframes are available for download.",
        )

    try:
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for kf in valid_frames:
                # Add file inside zip with clear descriptive filename
                zipf.write(kf.image_path, arcname=kf.image_filename)

        logger.info(
            "Created keyframe ZIP archive with %d images: %s",
            len(valid_frames),
            output_zip_path.name,
        )
        return output_zip_path
    except Exception as e:
        logger.error("Failed creating ZIP archive: %s", e)
        raise ExportError(f"Failed to create keyframes archive: {e}")


def create_video_clips_zip(
    scenes: List[SceneInfo],
    output_zip_path: Path,
) -> Path:
    """Packages all generated individual scene video clips into a compressed ZIP archive."""
    output_zip_path = Path(output_zip_path).resolve()
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)

    valid_clips = []
    for s in scenes:
        if s.clip_path and Path(s.clip_path).exists():
            valid_clips.append((Path(s.clip_path), s.clip_filename or Path(s.clip_path).name))

    if not valid_clips:
        raise ExportError(
            "No video clips found to package into ZIP archive.",
            user_friendly_message="No scene video clips are available for download.",
        )

    try:
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for clip_path, arc_name in valid_clips:
                zipf.write(clip_path, arcname=arc_name)

        logger.info(
            "Created video clips ZIP archive with %d video clips: %s",
            len(valid_clips),
            output_zip_path.name,
        )
        return output_zip_path
    except Exception as e:
        logger.error("Failed creating video clips ZIP: %s", e)
        raise ExportError(f"Failed to create video clips archive: {e}")


def export_scenes_csv(scenes: List[SceneInfo], output_csv_path: Path) -> Path:
    """Exports detected scenes and timing data to a standardized CSV format."""
    output_csv_path = Path(output_csv_path).resolve()
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "scene_number",
        "start_frame",
        "end_frame",
        "start_time_seconds",
        "end_time_seconds",
        "duration_seconds",
        "start_timecode",
        "end_timecode",
        "duration_timecode",
        "keyframe_frame",
        "keyframe_timecode",
        "pacing_label",
    ]

    try:
        with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for s in scenes:
                writer.writerow(s.to_dict())

        logger.info("Exported scene CSV to %s", output_csv_path.name)
        return output_csv_path
    except Exception as e:
        logger.error("Failed exporting scene CSV: %s", e)
        raise ExportError(f"Failed to export scene CSV: {e}")


def export_summary_json(
    metadata: VideoMetadata,
    summary: VideoSummaryReport,
    scenes: List[SceneInfo],
    output_json_path: Path,
    narrative: Optional[Any] = None,
) -> Path:
    """Exports complete metadata, summary metrics, and scene list to structured JSON."""
    output_json_path = Path(output_json_path).resolve()
    output_json_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metadata": metadata.to_dict(),
        "summary": summary.to_dict(),
        "narrative": narrative.to_dict() if narrative else None,
        "scenes": [s.to_dict() for s in scenes],
    }

    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        logger.info("Exported analysis JSON to %s", output_json_path.name)
        return output_json_path
    except Exception as e:
        logger.error("Failed exporting summary JSON: %s", e)
        raise ExportError(f"Failed to export JSON report: {e}")


def export_summary_markdown(
    metadata: VideoMetadata,
    summary: VideoSummaryReport,
    scenes: List[SceneInfo],
    output_md_path: Path,
    narrative: Optional[Any] = None,
) -> Path:
    """Generates a clean, formatted Markdown report of video analysis results."""
    output_md_path = Path(output_md_path).resolve()
    output_md_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {narrative.title_suggestion if narrative else 'ClipMind AI — Video Intelligence Report'}",
        "",
        f"**File Analyzed:** `{metadata.filename}`  ",
        f"**Resolution:** {metadata.width}x{metadata.height} ({metadata.aspect_ratio})  ",
        f"**Frame Rate:** {metadata.fps} fps  ",
        f"**Total Duration:** {metadata.duration_formatted} ({metadata.duration_seconds}s)  ",
        f"**Codec:** {metadata.fourcc_codec}  ",
        f"**File Size:** {metadata.file_size_mb} MB  ",
        "",
    ]

    if narrative:
        lines.extend([
            "---",
            "",
            "## Executive Narrative & Visual Atmosphere",
            "",
            f"**Synopsis:** {narrative.executive_synopsis}  ",
            f"**Visual Atmosphere:** {narrative.visual_atmosphere}  ",
            f"**Primary Mood:** {narrative.primary_mood}  ",
            f"**Tempo Rhythm:** {narrative.tempo_rhythm_summary}  ",
            f"**Dominant Color Palette:** {', '.join(narrative.dominant_palette_hex)}  ",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## Scene & Pacing Analytics",
        "",
        f"- **Total Detected Scenes:** {summary.total_scenes}",
        f"- **Average Scene Duration:** {summary.avg_scene_duration_seconds}s ({summary.avg_scene_duration_formatted})",
        f"- **Scene Frequency:** {summary.scenes_per_minute} scenes/minute",
        f"- **Rapid Cuts (<2s):** {summary.rapid_scenes_count} ({summary.rapid_scenes_pct}%)",
        f"- **Standard Takes (2-8s):** {summary.standard_scenes_count} ({summary.standard_scenes_pct}%)",
        f"- **Extended Takes (>8s):** {summary.extended_scenes_count} ({summary.extended_scenes_pct}%)",
        f"- **Extracted Keyframes:** {summary.extracted_keyframes_count} ({summary.unique_keyframes_count} unique)",
        "",
        "---",
        "",
        "## Narrative & Structural Breakdown",
        "",
    ])

    for item in summary.narrative_breakdown:
        lines.append(f"### {item['phase']}")
        lines.append(f"- **Scenes:** {item['scenes_range']}")
        lines.append(f"- **Timecodes:** {item['timecode_range']}")
        lines.append(f"- **Observation:** {item['description']}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Scene Index Table",
        "",
        "| Scene # | Start Time | End Time | Duration | Pacing | Keyframe Timecode |",
        "| :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    for s in scenes:
        lines.append(
            f"| {s.scene_number:02d} | {s.start_timecode} | {s.end_timecode} | "
            f"{s.duration_seconds:.2f}s | {s.pacing_label} | {s.keyframe_timecode or 'N/A'} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Methodology & Verification Note",
        "",
        summary.methodology_note,
        "",
        "*Report generated automatically by ClipMind AI.*",
    ])

    try:
        output_md_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Exported Markdown report to %s", output_md_path.name)
        return output_md_path
    except Exception as e:
        logger.error("Failed exporting Markdown report: %s", e)
        raise ExportError(f"Failed to export Markdown report: {e}")
