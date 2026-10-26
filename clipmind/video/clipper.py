"""Frame-accurate video clipping engine for extracting individual scene cuts."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Callable, List, Optional

import cv2

from clipmind.config import config
from clipmind.exceptions import CorruptedVideoError
from clipmind.logger import logger
from clipmind.video.detector import SceneInfo, seconds_to_timecode


def extract_scene_clips(
    video_path: Path,
    scenes: List[SceneInfo],
    output_dir: Path,
    max_clips: Optional[int] = 50,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> List[Path]:
    """Slices a video into frame-accurate individual scene video clips (.mp4).

    Args:
        video_path: Source video file path.
        scenes: List of detected SceneInfo objects with start_frame and end_frame.
        output_dir: Directory where individual scene clips will be written.
        max_clips: Maximum number of scene clips to generate (to avoid disk exhaustion).
        progress_callback: Optional progress reporter callback.

    Returns:
        List of Paths to the generated scene video clips.
    """
    video_path = Path(video_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not scenes:
        logger.warning("No scenes provided for video clipping.")
        return []

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise CorruptedVideoError(f"Cannot open video for scene clipping: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0.0 or math.isnan(fps):
        fps = 30.0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Standard browser-compatible MP4 codec
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    target_scenes = scenes[:max_clips] if max_clips else scenes
    total_target = len(target_scenes)
    clip_paths: List[Path] = []

    try:
        for idx, scene in enumerate(target_scenes, start=1):
            start_f = max(0, scene.start_frame)
            end_f = min(total_frames, max(start_f + 1, scene.end_frame))

            # Name format: scene_001_cut_00-00-00_to_00-00-05.mp4
            start_slug = scene.start_timecode.replace(":", "-").replace(".", "_")
            end_slug = scene.end_timecode.replace(":", "-").replace(".", "_")
            clip_name = f"scene_{scene.scene_number:03d}_cut_{start_slug}_to_{end_slug}.mp4"
            clip_path = output_dir / clip_name

            # Position reader at exact start frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)
            writer = cv2.VideoWriter(str(clip_path), fourcc, fps, (width, height))

            written_frames = 0
            curr_frame = start_f
            while curr_frame < end_f:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break
                writer.write(frame)
                written_frames += 1
                curr_frame += 1

            writer.release()

            # Record file metadata onto SceneInfo
            if clip_path.exists() and clip_path.stat().st_size > 0:
                scene.clip_path = str(clip_path)
                scene.clip_filename = clip_name
                scene.clip_size_mb = round(clip_path.stat().st_size / (1024 * 1024), 2)
                clip_paths.append(clip_path)
                logger.info(
                    "Extracted scene clip %d/%d: %s (%d frames, %.2f MB)",
                    idx,
                    total_target,
                    clip_name,
                    written_frames,
                    scene.clip_size_mb,
                )
            else:
                logger.warning("Scene clip %s was empty or failed to write", clip_name)

            if progress_callback:
                progress = (idx / total_target)
                progress_callback(progress, f"Generating scene clip {idx}/{total_target}...")

    finally:
        cap.release()

    return clip_paths
