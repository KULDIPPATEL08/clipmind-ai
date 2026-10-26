"""Scene boundary detection using PySceneDetect with OpenCV fallback."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
from scenedetect import ContentDetector, AdaptiveDetector, ThresholdDetector, SceneManager, open_video

from clipmind.config import config
from clipmind.exceptions import CorruptedVideoError, SceneDetectionError
from clipmind.logger import logger
from clipmind.video.metadata import VideoMetadata, extract_video_metadata, format_duration


@dataclass
class SceneInfo:
    """Detailed metadata for an individual detected scene."""

    scene_number: int
    start_frame: int
    end_frame: int
    start_time_seconds: float
    end_time_seconds: float
    duration_seconds: float
    start_timecode: str
    end_timecode: str
    duration_timecode: str
    keyframe_frame: Optional[int] = None
    keyframe_time_seconds: Optional[float] = None
    keyframe_timecode: Optional[str] = None
    keyframe_path: Optional[str] = None
    pacing_label: str = "normal"  # "rapid (<2s)", "normal (2-8s)", "long (>8s)"

    def to_dict(self) -> Dict[str, Any]:
        """Convert scene information to dictionary."""
        return asdict(self)


def seconds_to_timecode(seconds: float) -> str:
    """Converts seconds into precision timecode HH:MM:SS.mmm."""
    if seconds < 0:
        seconds = 0.0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hours:02d}:{minutes:02d}:{sec:02d}.{millis:03d}"


def get_pacing_label(duration: float) -> str:
    """Classifies scene pace based on duration."""
    if duration < 2.0:
        return "Rapid (<2s)"
    elif duration > 8.0:
        return "Extended (>8s)"
    return "Standard (2-8s)"


class VideoSceneDetector:
    """Detects scene cuts and transitions in video files."""

    def __init__(
        self,
        detector_type: str = "content",
        threshold: float = 27.0,
        min_scene_len_frames: int = 15,
    ) -> None:
        self.detector_type = detector_type.lower()
        self.threshold = threshold
        self.min_scene_len_frames = max(1, min_scene_len_frames)

    def _build_scenedetect_detector(self):
        """Builds the configured PySceneDetect detector instance."""
        if self.detector_type == "adaptive":
            return AdaptiveDetector(
                adaptive_threshold=self.threshold,
                min_scene_len=self.min_scene_len_frames,
            )
        elif self.detector_type == "threshold":
            return ThresholdDetector(
                threshold=self.threshold,
                min_scene_len=self.min_scene_len_frames,
            )
        else:
            # Default to ContentDetector
            return ContentDetector(
                threshold=self.threshold,
                min_scene_len=self.min_scene_len_frames,
            )

    def detect_scenes(
        self,
        video_path: Path,
        metadata: Optional[VideoMetadata] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> List[SceneInfo]:
        """Runs scene detection on the video using PySceneDetect, with OpenCV fallback.

        Args:
            video_path: Path to validated video file.
            metadata: Pre-extracted video metadata, or will be extracted if None.
            progress_callback: Optional callback func(progress_ratio, status_message).

        Returns:
            List of detected SceneInfo objects.
        """
        video_path = Path(video_path).resolve()
        meta = metadata or extract_video_metadata(video_path)

        if progress_callback:
            progress_callback(0.1, "Initializing scene detector...")

        # Try PySceneDetect first
        try:
            scenes = self._detect_with_scenedetect(video_path, meta, progress_callback)
            if scenes:
                logger.info(
                    "PySceneDetect found %d scenes in %s",
                    len(scenes),
                    video_path.name,
                )
                return scenes
        except Exception as e:
            logger.warning(
                "PySceneDetect encountered error: %s. Falling back to OpenCV differential detector.",
                str(e),
            )

        # Fallback to custom OpenCV difference detector
        if progress_callback:
            progress_callback(0.3, "Running fallback frame-difference detector...")
        return self._detect_with_opencv_fallback(video_path, meta, progress_callback)

    def _detect_with_scenedetect(
        self,
        video_path: Path,
        meta: VideoMetadata,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> List[SceneInfo]:
        """Detects scenes using PySceneDetect's SceneManager."""
        video = open_video(str(video_path))
        scene_manager = SceneManager()
        scene_manager.add_detector(self._build_scenedetect_detector())

        if progress_callback:
            progress_callback(0.3, "Analyzing video frames for scene transitions...")

        scene_manager.detect_scenes(video=video)
        scene_list = scene_manager.get_scene_list()

        results: List[SceneInfo] = []
        fps = meta.fps if meta.fps > 0 else 30.0

        if not scene_list:
            # Entire video treated as a single scene
            duration = meta.duration_seconds
            results.append(
                SceneInfo(
                    scene_number=1,
                    start_frame=0,
                    end_frame=meta.total_frames,
                    start_time_seconds=0.0,
                    end_time_seconds=duration,
                    duration_seconds=duration,
                    start_timecode=seconds_to_timecode(0.0),
                    end_timecode=seconds_to_timecode(duration),
                    duration_timecode=format_duration(duration),
                    pacing_label=get_pacing_label(duration),
                )
            )
            return results

        # Enforce maximum scenes cap to prevent memory exhaustion
        capped_scenes = scene_list[: config.max_scenes_limit]

        for idx, (start_time, end_time) in enumerate(capped_scenes, start=1):
            start_frame = getattr(start_time, "frame_num", None)
            if start_frame is None:
                start_frame = start_time.get_frames()

            end_frame = getattr(end_time, "frame_num", None)
            if end_frame is None:
                end_frame = end_time.get_frames()

            start_sec = getattr(start_time, "seconds", None)
            if start_sec is None:
                start_sec = start_time.get_seconds()

            end_sec = getattr(end_time, "seconds", None)
            if end_sec is None:
                end_sec = end_time.get_seconds()

            duration = max(0.01, end_sec - start_sec)

            results.append(
                SceneInfo(
                    scene_number=idx,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    start_time_seconds=round(start_sec, 3),
                    end_time_seconds=round(end_sec, 3),
                    duration_seconds=round(duration, 3),
                    start_timecode=seconds_to_timecode(start_sec),
                    end_timecode=seconds_to_timecode(end_sec),
                    duration_timecode=format_duration(duration),
                    pacing_label=get_pacing_label(duration),
                )
            )

        if progress_callback:
            progress_callback(0.7, f"Identified {len(results)} scenes.")

        return results

    def _detect_with_opencv_fallback(
        self,
        video_path: Path,
        meta: VideoMetadata,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> List[SceneInfo]:
        """Custom CPU-friendly OpenCV frame differencing detector."""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise CorruptedVideoError(f"Cannot open video for fallback detection: {video_path}")

        fps = meta.fps if meta.fps > 0 else 30.0
        total_frames = meta.total_frames
        sample_step = max(1, int(fps / 5))  # Sample ~5 times a second for speed

        scene_cut_frames = [0]
        prev_hist = None
        frame_idx = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                if frame_idx % sample_step == 0:
                    # Resize to low-res thumbnail for lightning-fast histogram computation
                    small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
                    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
                    hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
                    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

                    if prev_hist is not None:
                        # Correlation comparison: lower correlation means bigger visual change
                        corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                        if corr < 0.65 and (frame_idx - scene_cut_frames[-1]) >= self.min_scene_len_frames:
                            scene_cut_frames.append(frame_idx)
                            if len(scene_cut_frames) >= config.max_scenes_limit:
                                break

                    prev_hist = hist

                frame_idx += 1
                if progress_callback and total_frames > 0 and frame_idx % 60 == 0:
                    ratio = 0.3 + 0.4 * min(1.0, frame_idx / total_frames)
                    progress_callback(ratio, f"Scanning frames ({frame_idx}/{total_frames})...")

        finally:
            cap.release()

        # Build SceneInfo intervals
        scene_cut_frames.append(max(frame_idx, total_frames))
        results: List[SceneInfo] = []

        for i in range(len(scene_cut_frames) - 1):
            s_frame = scene_cut_frames[i]
            e_frame = scene_cut_frames[i + 1]
            s_sec = s_frame / fps
            e_sec = e_frame / fps
            duration = max(0.01, e_sec - s_sec)

            results.append(
                SceneInfo(
                    scene_number=i + 1,
                    start_frame=s_frame,
                    end_frame=e_frame,
                    start_time_seconds=round(s_sec, 3),
                    end_time_seconds=round(e_sec, 3),
                    duration_seconds=round(duration, 3),
                    start_timecode=seconds_to_timecode(s_sec),
                    end_timecode=seconds_to_timecode(e_sec),
                    duration_timecode=format_duration(duration),
                    pacing_label=get_pacing_label(duration),
                )
            )

        return results
