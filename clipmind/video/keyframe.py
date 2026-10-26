"""Timestamped keyframe extraction, deduplication, and visual contact sheet generation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from clipmind.config import config
from clipmind.exceptions import CorruptedVideoError, KeyframeExtractionError
from clipmind.logger import logger
from clipmind.video.detector import SceneInfo, seconds_to_timecode


@dataclass
class Keyframe:
    """Extracted keyframe representation."""

    scene_number: int
    frame_index: int
    timestamp_seconds: float
    timecode: str
    image_path: Path
    image_filename: str
    width: int
    height: int
    is_duplicate: bool = False


class KeyframeExtractor:
    """Extracts representative, timestamped keyframes and builds contact sheets."""

    def __init__(
        self,
        strategy: str = "middle",
        enable_deduplication: bool = True,
        dedup_threshold: float = 0.92,
        max_keyframes: Optional[int] = None,
    ) -> None:
        self.strategy = strategy.lower()
        self.enable_deduplication = enable_deduplication
        self.dedup_threshold = dedup_threshold
        self.max_keyframes = max_keyframes or config.max_keyframes_limit

    def extract_keyframes(
        self,
        video_path: Path,
        scenes: List[SceneInfo],
        output_dir: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> List[Keyframe]:
        """Extracts representative keyframes for all detected scenes.

        Args:
            video_path: Path to the video file.
            scenes: List of detected SceneInfo objects.
            output_dir: Directory where keyframe image files will be saved.
            progress_callback: Optional progress reporter callback.

        Returns:
            List of Keyframe objects.
        """
        video_path = Path(video_path).resolve()
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        if not scenes:
            logger.warning("No scenes provided for keyframe extraction.")
            return []

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise CorruptedVideoError(f"Cannot open video for keyframe extraction: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0.0 or math.isnan(fps):
            fps = 30.0

        keyframes: List[Keyframe] = []
        extracted_histograms: List[np.ndarray] = []

        total_scenes = min(len(scenes), self.max_keyframes)
        target_scenes = scenes[:total_scenes]

        try:
            for idx, scene in enumerate(target_scenes, start=1):
                # Determine target frame number based on strategy
                target_frame = self._select_frame_index(scene)
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                ret, frame = cap.read()

                # Fallback if frame read failed: try reading scene start
                if not ret or frame is None:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, scene.start_frame)
                    ret, frame = cap.read()

                if not ret or frame is None:
                    logger.warning("Could not read frame %d for scene %d", target_frame, scene.scene_number)
                    continue

                h, w = frame.shape[:2]
                sec = target_frame / fps
                timecode_str = seconds_to_timecode(sec)

                # Deduplication check via HSV color histogram
                is_duplicate = False
                if self.enable_deduplication:
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
                    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

                    for prev_hist in extracted_histograms:
                        similarity = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                        if similarity >= self.dedup_threshold:
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        extracted_histograms.append(hist)

                # Format filename: scene_001_00-00-12.jpg
                safe_time_slug = timecode_str.replace(":", "-").replace(".", "_")
                img_name = f"scene_{scene.scene_number:03d}_{safe_time_slug}.jpg"
                img_path = output_dir / img_name

                # Save image using OpenCV (JPEG quality 92)
                cv2.imwrite(str(img_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])

                # Update scene info with keyframe details
                scene.keyframe_frame = target_frame
                scene.keyframe_time_seconds = round(sec, 3)
                scene.keyframe_timecode = timecode_str
                scene.keyframe_path = str(img_path)

                kf = Keyframe(
                    scene_number=scene.scene_number,
                    frame_index=target_frame,
                    timestamp_seconds=round(sec, 3),
                    timecode=timecode_str,
                    image_path=img_path,
                    image_filename=img_name,
                    width=w,
                    height=h,
                    is_duplicate=is_duplicate,
                )
                keyframes.append(kf)

                if progress_callback:
                    ratio = 0.7 + 0.25 * (idx / total_scenes)
                    progress_callback(ratio, f"Extracting keyframe {idx}/{total_scenes}...")

        finally:
            cap.release()

        logger.info(
            "Extracted %d keyframes (%d duplicates detected) into %s",
            len(keyframes),
            sum(1 for k in keyframes if k.is_duplicate),
            output_dir,
        )
        return keyframes

    def _select_frame_index(self, scene: SceneInfo) -> int:
        """Selects the frame index within the scene based on chosen strategy."""
        start = scene.start_frame
        end = max(start + 1, scene.end_frame)

        if self.strategy == "start":
            # Pick a couple frames in to avoid cross-fade boundary
            return min(start + 2, end - 1)
        elif self.strategy == "end":
            return max(start, end - 2)
        else:
            # Middle frame is the most reliable representation
            return (start + end) // 2


def generate_contact_sheet(
    keyframes: List[Keyframe],
    output_path: Path,
    columns: int = 4,
    thumb_width: int = 320,
    include_duplicates: bool = False,
) -> Optional[Path]:
    """Assembles a high-resolution visual contact sheet / storyboard grid from keyframes.

    Args:
        keyframes: List of extracted keyframes.
        output_path: Destination path for the saved contact sheet image.
        columns: Number of grid columns.
        thumb_width: Width of each thumbnail.
        include_duplicates: Whether to include duplicate flagged frames.

    Returns:
        Path to the saved contact sheet or None if no valid keyframes.
    """
    valid_frames = [
        k for k in keyframes if k.image_path.exists() and (include_duplicates or not k.is_duplicate)
    ]
    if not valid_frames:
        logger.warning("No valid keyframes to generate contact sheet.")
        return None

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    n_items = len(valid_frames)
    cols = min(columns, n_items)
    rows = math.ceil(n_items / cols)

    # Compute thumbnail dimensions preserving 16:9 standard ratio if height varies
    first_img = Image.open(valid_frames[0].image_path)
    aspect = first_img.height / max(1, first_img.width)
    first_img.close()

    thumb_height = int(thumb_width * aspect)
    caption_height = 34
    cell_width = thumb_width + 12
    cell_height = thumb_height + caption_height + 12

    total_width = cols * cell_width + 16
    header_height = 60
    total_height = rows * cell_height + header_height + 16

    # Create dark-themed storyboard canvas
    canvas = Image.new("RGB", (total_width, total_height), color=(18, 20, 26))
    draw = ImageDraw.Draw(canvas)

    # Draw Header
    title_text = f"ClipMind AI — Video Storyboard Summary ({n_items} Scenes)"
    draw.text((20, 18), title_text, fill=(240, 243, 246))

    for idx, kf in enumerate(valid_frames):
        c = idx % cols
        r = idx // cols
        x = 16 + c * cell_width
        y = header_height + 12 + r * cell_height

        try:
            with Image.open(kf.image_path) as img:
                thumb = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                canvas.paste(thumb, (x, y))

            # Draw card frame border
            draw.rectangle(
                [x - 1, y - 1, x + thumb_width + 1, y + thumb_height + caption_height + 1],
                outline=(45, 52, 65),
                width=1,
            )

            # Draw badge background for timestamp
            draw.rectangle(
                [x, y + thumb_height, x + thumb_width, y + thumb_height + caption_height],
                fill=(26, 31, 40),
            )

            label = f"#{kf.scene_number:02d}  •  {kf.timecode}"
            draw.text((x + 8, y + thumb_height + 9), label, fill=(180, 195, 215))

        except Exception as e:
            logger.warning("Failed to render thumbnail for scene %d: %s", kf.scene_number, e)

    canvas.save(output_path, "JPEG", quality=90)
    logger.info("Generated visual contact sheet: %s (%dx%d)", output_path.name, total_width, total_height)
    return output_path
