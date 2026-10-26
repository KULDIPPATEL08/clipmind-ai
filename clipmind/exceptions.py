"""Custom domain exceptions for ClipMind AI with safe user messaging."""

from __future__ import annotations


class ClipMindError(Exception):
    """Base exception for all ClipMind application errors."""

    def __init__(self, message: str, user_friendly_message: str | None = None) -> None:
        super().__init__(message)
        self.user_friendly_message = user_friendly_message or (
            "An unexpected error occurred during processing. Please try again with a valid video."
        )


class SecurityValidationError(ClipMindError):
    """Raised when file upload violates security constraints (size, path, mime)."""

    def __init__(self, message: str, user_friendly_message: str | None = None) -> None:
        safe_msg = user_friendly_message or "Uploaded file failed security checks."
        super().__init__(message, user_friendly_message=safe_msg)


class UnsupportedFormatError(ClipMindError):
    """Raised when an uploaded file format is not supported or lacks video streams."""

    def __init__(self, message: str, user_friendly_message: str | None = None) -> None:
        safe_msg = (
            user_friendly_message
            or "The uploaded file format is not supported. Please upload MP4, MOV, AVI, MKV, or WEBM."
        )
        super().__init__(message, user_friendly_message=safe_msg)


class CorruptedVideoError(ClipMindError):
    """Raised when video file headers or frames cannot be decoded."""

    def __init__(self, message: str, user_friendly_message: str | None = None) -> None:
        safe_msg = (
            user_friendly_message
            or "The video file appears corrupted and could not be decoded. Please verify the file plays locally."
        )
        super().__init__(message, user_friendly_message=safe_msg)


class SceneDetectionError(ClipMindError):
    """Raised when scene detection fails during analysis."""

    def __init__(self, message: str, user_friendly_message: str | None = None) -> None:
        safe_msg = (
            user_friendly_message
            or "Scene detection failed during video analysis. Try adjusting sensitivity settings."
        )
        super().__init__(message, user_friendly_message=safe_msg)


class KeyframeExtractionError(ClipMindError):
    """Raised when keyframe extraction cannot obtain valid frames."""

    def __init__(self, message: str, user_friendly_message: str | None = None) -> None:
        safe_msg = (
            user_friendly_message
            or "Could not extract representative keyframes from the detected scenes."
        )
        super().__init__(message, user_friendly_message=safe_msg)


class ExportError(ClipMindError):
    """Raised when generating ZIP, CSV, or visual report exports fails."""

    def __init__(self, message: str, user_friendly_message: str | None = None) -> None:
        safe_msg = user_friendly_message or "Failed to generate export package."
        super().__init__(message, user_friendly_message=safe_msg)
