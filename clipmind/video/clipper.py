"""Frame-accurate video clipping engine with audio/sound preservation and custom time trimming."""

from __future__ import annotations

import math
from pathlib import Path
import subprocess
from typing import Callable, List, Optional

import cv2

from clipmind.config import config
from clipmind.exceptions import CorruptedVideoError
from clipmind.logger import logger
from clipmind.video.detector import SceneInfo, seconds_to_timecode


def get_ffmpeg_binary() -> Optional[str]:
    """Resolves path to working ffmpeg executable (imageio_ffmpeg or system)."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return str(exe)
    except Exception as e:
        logger.debug("imageio_ffmpeg not found: %s", e)

    import shutil
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg

    return None


def extract_single_custom_clip(
    video_path: Path,
    start_seconds: float,
    end_seconds: float,
    output_path: Path,
) -> bool:
    """Extracts a custom trimmed video clip with full audio preservation and highest quality.

    Args:
        video_path: Source video path.
        start_seconds: Start timestamp in seconds.
        end_seconds: End timestamp in seconds.
        output_path: Destination path for the extracted mp4 file.

    Returns:
        True if clip successfully generated, False otherwise.
    """
    video_path = Path(video_path).resolve()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    duration = max(0.2, end_seconds - start_seconds)
    ffmpeg_exe = get_ffmpeg_binary()

    if ffmpeg_exe:
        try:
            cmd = [
                ffmpeg_exe,
                "-y",
                "-ss", f"{start_seconds:.3f}",
                "-i", str(video_path),
                "-t", f"{duration:.3f}",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(output_path),
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45,
            )
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                logger.info("Custom clip extracted with full audio via FFmpeg: %s", output_path.name)
                return True
        except Exception as e:
            logger.warning("FFmpeg custom clip extraction failed, falling back to OpenCV: %s", e)

    # OpenCV Fallback
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return False

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    start_frame = int(start_seconds * fps)
    end_frame = int(end_seconds * fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    curr_f = start_frame
    while curr_f < end_frame:
        ret, frame = cap.read()
        if not ret or frame is None:
            break
        writer.write(frame)
        curr_f += 1

    writer.release()
    cap.release()
    return output_path.exists() and output_path.stat().st_size > 0


def extract_scene_clips(
    video_path: Path,
    scenes: List[SceneInfo],
    output_dir: Path,
    max_clips: Optional[int] = 50,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> List[Path]:
    """Slices a video into frame-accurate individual scene video clips (.mp4) with audio preservation.

    Args:
        video_path: Source video file path.
        scenes: List of detected SceneInfo objects with start_frame and end_frame.
        output_dir: Directory where individual scene clips will be written.
        max_clips: Maximum number of scene clips to generate.
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

    target_scenes = scenes[:max_clips] if max_clips else scenes
    total_target = len(target_scenes)
    clip_paths: List[Path] = []
    ffmpeg_exe = get_ffmpeg_binary()

    # Try FFmpeg batch clipping for lossless sound preservation
    if ffmpeg_exe:
        logger.info("Using FFmpeg (%s) for audio-preserved scene clipping", ffmpeg_exe)
        for idx, scene in enumerate(target_scenes, start=1):
            start_slug = scene.start_timecode.replace(":", "-").replace(".", "_")
            end_slug = scene.end_timecode.replace(":", "-").replace(".", "_")
            clip_name = f"scene_{scene.scene_number:03d}_cut_{start_slug}_to_{end_slug}.mp4"
            clip_path = output_dir / clip_name

            duration = max(0.1, scene.duration_seconds)
            try:
                cmd = [
                    ffmpeg_exe,
                    "-y",
                    "-ss", f"{scene.start_time_seconds:.3f}",
                    "-i", str(video_path),
                    "-t", f"{duration:.3f}",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "18",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    str(clip_path),
                ]
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30,
                )
                if proc.returncode == 0 and clip_path.exists() and clip_path.stat().st_size > 0:
                    scene.clip_path = str(clip_path)
                    scene.clip_filename = clip_name
                    scene.clip_size_mb = round(clip_path.stat().st_size / (1024 * 1024), 2)
                    clip_paths.append(clip_path)
            except Exception as e:
                logger.warning("FFmpeg cut failed for scene %d: %s. Falling back to OpenCV.", idx, e)

            if progress_callback:
                progress_callback(idx / total_target, f"Extracting scene clip {idx}/{total_target} (Audio Active)...")

        # If all or most clips succeeded via FFmpeg, return early
        if len(clip_paths) == total_target:
            return clip_paths

    # OpenCV Fallback for any missing clips
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        if clip_paths:
            return clip_paths
        raise CorruptedVideoError(f"Cannot open video for scene clipping: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    try:
        for idx, scene in enumerate(target_scenes, start=1):
            if scene.clip_path and Path(scene.clip_path).exists():
                continue

            start_f = max(0, scene.start_frame)
            end_f = min(total_frames, max(start_f + 1, scene.end_frame))

            start_slug = scene.start_timecode.replace(":", "-").replace(".", "_")
            end_slug = scene.end_timecode.replace(":", "-").replace(".", "_")
            clip_name = f"scene_{scene.scene_number:03d}_cut_{start_slug}_to_{end_slug}.mp4"
            clip_path = output_dir / clip_name

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

            if clip_path.exists() and clip_path.stat().st_size > 0:
                scene.clip_path = str(clip_path)
                scene.clip_filename = clip_name
                scene.clip_size_mb = round(clip_path.stat().st_size / (1024 * 1024), 2)
                clip_paths.append(clip_path)
    finally:
        cap.release()

    return clip_paths
