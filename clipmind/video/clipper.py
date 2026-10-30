"""Frame-accurate video clipping engine with audio/sound preservation and custom time trimming."""

from __future__ import annotations

import math
from pathlib import Path
import subprocess
from typing import Any, Callable, Dict, List, Optional

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
    aspect_ratio: str = "original",
    **kwargs: Any,
) -> bool:
    """Extracts a custom trimmed video clip with full audio preservation and optional 9:16 vertical portrait formatting.

    Args:
        video_path: Source video path.
        start_seconds: Start timestamp in seconds.
        end_seconds: End timestamp in seconds.
        output_path: Destination path for the extracted mp4 file.
        aspect_ratio: Layout format: 'original', '9:16_blurred' (Shorts/Reels with blurred background),
            or '9:16_crop' (center cropped full 9:16).

    Returns:
        True if clip successfully generated, False otherwise.
    """
    video_path = Path(video_path).resolve()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure boundaries are properly ordered and non-negative
    if start_seconds > end_seconds:
        start_seconds, end_seconds = end_seconds, start_seconds
    start_seconds = max(0.0, float(start_seconds))
    end_seconds = max(start_seconds + 0.1, float(end_seconds))
    duration = max(0.1, end_seconds - start_seconds)

    ffmpeg_exe = get_ffmpeg_binary()

    if ffmpeg_exe:
        # If original aspect ratio requested, try lightning-fast lossless stream copy first (-c copy)
        if aspect_ratio == "original":
            try:
                fast_cmd = [
                    ffmpeg_exe,
                    "-y",
                    "-ss", f"{start_seconds:.3f}",
                    "-i", str(video_path),
                    "-t", f"{duration:.3f}",
                    "-c", "copy",
                    "-movflags", "+faststart",
                    str(output_path),
                ]
                res_fast = subprocess.run(
                    fast_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=15,
                )
                if res_fast.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                    logger.info("Custom clip extracted losslessly via FFmpeg copy: %s", output_path.name)
                    return True
            except Exception as e_copy:
                logger.debug("Fast stream-copy trim failed (%s), attempting full re-encode", e_copy)

        # Build FFmpeg command with portrait filters or standard encoding
        try:
            cmd = [
                ffmpeg_exe,
                "-y",
                "-ss", f"{start_seconds:.3f}",
                "-i", str(video_path),
                "-t", f"{duration:.3f}",
            ]

            if aspect_ratio == "9:16_blurred":
                # Professional YouTube Shorts / TikTok blurred background fill (1080x1920)
                filter_complex = (
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                    "boxblur=25:5[bg];"
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
                    "[bg][fg]overlay=(W-w)/2:(H-h)/2"
                )
                cmd.extend(["-filter_complex", filter_complex])
            elif aspect_ratio == "9:16_crop":
                # Full center crop to 9:16 vertical ratio (1080x1920)
                vf_crop = "crop=w='min(iw,ih*9/16)':h='min(ih,iw*16/9)':x='(iw-ow)/2':y='(ih-oh)/2',scale=1080:1920"
                cmd.extend(["-vf", vf_crop])

            cmd.extend([
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(output_path),
            ])

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180,
            )
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                logger.info("Custom clip extracted (%s) with audio via FFmpeg: %s", aspect_ratio, output_path.name)
                return True
            else:
                logger.warning("FFmpeg command returned error: %s", result.stderr)
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

    is_portrait = aspect_ratio in ["9:16_blurred", "9:16_crop", "9:16"]
    out_w, out_h = (1080, 1920) if is_portrait else (width, height)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (out_w, out_h))

    curr_f = start_frame
    while curr_f < end_frame:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        if aspect_ratio == "9:16_crop":
            crop_w = int(height * 9 / 16)
            if crop_w < width:
                start_x = max(0, (width - crop_w) // 2)
                frame = frame[:, start_x:start_x + crop_w]
            frame = cv2.resize(frame, (1080, 1920))
        elif aspect_ratio == "9:16_blurred":
            bg = cv2.resize(frame, (1080, 1920))
            bg = cv2.GaussianBlur(bg, (51, 51), 0)
            h_factor = 1080.0 / max(1, width)
            fg_w = 1080
            fg_h = int(height * h_factor)
            if fg_h > 1920:
                fg_h = 1920
                fg_w = int(width * (1920.0 / max(1, height)))
            fg = cv2.resize(frame, (max(1, fg_w), max(1, fg_h)))
            y_off = max(0, (1920 - fg_h) // 2)
            x_off = max(0, (1080 - fg_w) // 2)
            bg[y_off:y_off + fg_h, x_off:x_off + fg_w] = fg
            frame = bg

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
    aspect_ratio: str = "original",
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs: Any,
) -> List[Path]:
    """Slices a video into frame-accurate individual scene video clips (.mp4) with audio preservation and optional 9:16 portrait layout.

    Args:
        video_path: Source video file path.
        scenes: List of detected SceneInfo objects with start_frame and end_frame.
        output_dir: Directory where individual scene clips will be written.
        max_clips: Maximum number of scene clips to generate.
        aspect_ratio: 'original', '9:16_blurred' (Shorts/Reels with blurred BG), or '9:16_crop'.
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

    fmt_suffix = "_portrait_9x16" if "9:16" in aspect_ratio else ""

    # Try FFmpeg batch clipping for lossless sound preservation
    if ffmpeg_exe:
        logger.info("Using FFmpeg (%s) for audio-preserved scene clipping (%s)", ffmpeg_exe, aspect_ratio)
        for idx, scene in enumerate(target_scenes, start=1):
            start_slug = scene.start_timecode.replace(":", "-").replace(".", "_")
            end_slug = scene.end_timecode.replace(":", "-").replace(".", "_")
            clip_name = f"scene_{scene.scene_number:03d}{fmt_suffix}_cut_{start_slug}_to_{end_slug}.mp4"
            clip_path = output_dir / clip_name

            duration = max(0.1, scene.duration_seconds)
            try:
                cmd = [
                    ffmpeg_exe,
                    "-y",
                    "-ss", f"{scene.start_time_seconds:.3f}",
                    "-i", str(video_path),
                    "-t", f"{duration:.3f}",
                ]

                if aspect_ratio == "9:16_blurred":
                    filter_complex = (
                        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                        "boxblur=25:5[bg];"
                        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
                        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
                    )
                    cmd.extend(["-filter_complex", filter_complex])
                elif aspect_ratio == "9:16_crop":
                    vf_crop = "crop=w='min(iw,ih*9/16)':h='min(ih,iw*16/9)':x='(iw-ow)/2':y='(ih-oh)/2',scale=1080:1920"
                    cmd.extend(["-vf", vf_crop])

                cmd.extend([
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "18",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    str(clip_path),
                ])

                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=45,
                )
                if proc.returncode == 0 and clip_path.exists() and clip_path.stat().st_size > 0:
                    scene.clip_path = str(clip_path)
                    scene.clip_filename = clip_name
                    scene.clip_size_mb = round(clip_path.stat().st_size / (1024 * 1024), 2)
                    clip_paths.append(clip_path)
            except Exception as e:
                logger.warning("FFmpeg cut failed for scene %d: %s. Falling back to OpenCV.", idx, e)

            if progress_callback:
                progress_callback(idx / total_target, f"Extracting scene clip {idx}/{total_target} ({aspect_ratio}, Audio Active)...")

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

    is_portrait = aspect_ratio in ["9:16_blurred", "9:16_crop", "9:16"]
    out_w, out_h = (1080, 1920) if is_portrait else (width, height)

    try:
        for idx, scene in enumerate(target_scenes, start=1):
            if scene.clip_path and Path(scene.clip_path).exists():
                continue

            start_f = max(0, scene.start_frame)
            end_f = min(total_frames, max(start_f + 1, scene.end_frame))

            start_slug = scene.start_timecode.replace(":", "-").replace(".", "_")
            end_slug = scene.end_timecode.replace(":", "-").replace(".", "_")
            clip_name = f"scene_{scene.scene_number:03d}{fmt_suffix}_cut_{start_slug}_to_{end_slug}.mp4"
            clip_path = output_dir / clip_name

            cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)
            writer = cv2.VideoWriter(str(clip_path), fourcc, fps, (out_w, out_h))

            curr_frame = start_f
            while curr_frame < end_f:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                if aspect_ratio == "9:16_crop":
                    crop_w = int(height * 9 / 16)
                    if crop_w < width:
                        start_x = max(0, (width - crop_w) // 2)
                        frame = frame[:, start_x:start_x + crop_w]
                    frame = cv2.resize(frame, (1080, 1920))
                elif aspect_ratio == "9:16_blurred":
                    bg = cv2.resize(frame, (1080, 1920))
                    bg = cv2.GaussianBlur(bg, (51, 51), 0)
                    h_factor = 1080.0 / max(1, width)
                    fg_w = 1080
                    fg_h = int(height * h_factor)
                    if fg_h > 1920:
                        fg_h = 1920
                        fg_w = int(width * (1920.0 / max(1, height)))
                    fg = cv2.resize(frame, (max(1, fg_w), max(1, fg_h)))
                    y_off = max(0, (1920 - fg_h) // 2)
                    x_off = max(0, (1080 - fg_w) // 2)
                    bg[y_off:y_off + fg_h, x_off:x_off + fg_w] = fg
                    frame = bg

                writer.write(frame)
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


def extract_fixed_interval_clips(
    video_path: Path,
    start_seconds: float,
    end_seconds: float,
    clip_duration_seconds: float,
    output_dir: Path,
    aspect_ratio: str = "original",
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs: Any,
) -> List[Dict[str, Any]]:
    """Slices a designated video time window into uniform fixed-duration clips (e.g. 60s clips).

    Args:
        video_path: Source video path.
        start_seconds: Ingestion start timestamp in seconds (e.g., 0.0s).
        end_seconds: Ingestion end timestamp in seconds (e.g., 350.0s).
        clip_duration_seconds: Fixed duration of each clip (e.g., 60.0s).
        output_dir: Directory where clips will be written.
        aspect_ratio: 'original', '9:16_blurred' (Shorts/Reels with blurred BG), or '9:16_crop'.
        progress_callback: Optional progress reporter callback.

    Returns:
        List of dictionaries with clip metadata (path, duration, timecodes, size).
    """
    video_path = Path(video_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if start_seconds > end_seconds:
        start_seconds, end_seconds = end_seconds, start_seconds
    start_seconds = max(0.0, float(start_seconds))
    end_seconds = max(start_seconds + 0.1, float(end_seconds))
    clip_duration_seconds = max(1.0, float(clip_duration_seconds))

    total_window = end_seconds - start_seconds
    if total_window <= 0.2:
        return []

    # Build discrete intervals
    intervals = []
    curr_start = start_seconds
    idx = 1
    while curr_start < end_seconds:
        curr_end = min(end_seconds, curr_start + clip_duration_seconds)
        if (curr_end - curr_start) >= 0.5:
            intervals.append((idx, curr_start, curr_end))
            idx += 1
        curr_start = curr_end

    if not intervals:
        return []

    results: List[Dict[str, Any]] = []
    total_count = len(intervals)

    format_tag = "shorts_portrait_9x16" if "9:16" in aspect_ratio else "landscape"

    for i, (clip_num, c_start, c_end) in enumerate(intervals, start=1):
        c_dur = c_end - c_start
        start_slug = seconds_to_timecode(c_start).replace(":", "-").replace(".", "_")
        end_slug = seconds_to_timecode(c_end).replace(":", "-").replace(".", "_")
        clip_name = f"interval_clip_{clip_num:03d}_{format_tag}_{int(c_dur)}s_{start_slug}_to_{end_slug}.mp4"
        clip_path = output_dir / clip_name

        if progress_callback:
            progress_callback(
                (i - 1) / total_count,
                f"Slicing clip {i}/{total_count} ({seconds_to_timecode(c_start)} ➔ {seconds_to_timecode(c_end)}, {format_tag})...",
            )

        success = extract_single_custom_clip(
            video_path=video_path,
            start_seconds=c_start,
            end_seconds=c_end,
            output_path=clip_path,
            aspect_ratio=aspect_ratio,
        )

        if success and clip_path.exists() and clip_path.stat().st_size > 0:
            results.append({
                "clip_index": clip_num,
                "start_sec": round(c_start, 2),
                "end_sec": round(c_end, 2),
                "duration_sec": round(c_dur, 2),
                "start_timecode": seconds_to_timecode(c_start),
                "end_timecode": seconds_to_timecode(c_end),
                "clip_path": str(clip_path),
                "clip_filename": clip_name,
                "aspect_ratio": aspect_ratio,
                "is_portrait": "9:16" in aspect_ratio,
                "size_mb": round(clip_path.stat().st_size / (1024 * 1024), 2),
            })

    if progress_callback:
        progress_callback(1.0, f"Generated {len(results)} clips ({format_tag})!")

    return results
