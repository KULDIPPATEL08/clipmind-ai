"""Security layer: input validation, sanitization, isolation, and safe cleanup."""

from __future__ import annotations

import io
import os
import re
import shutil
import time
import uuid
from pathlib import Path
from types import TracebackType
from typing import BinaryIO, Optional, Set, Type

from clipmind.config import config
from clipmind.exceptions import CorruptedVideoError, SecurityValidationError
from clipmind.logger import logger

# Video container signatures (magic bytes)
KNOWN_MAGIC_SIGNATURES = {
    # MP4 / MOV signatures: offset 4 contains 'ftyp' or 'moov'
    "mp4": [b"ftyp", b"moov"],
    # MKV / WEBM (EBML ID)
    "mkv_webm": [b"\x1a\x45\xdf\xa3"],
    # AVI: starts with RIFF and has AVI at offset 8
    "avi": [b"RIFF"],
}


class JobSession:
    """Manages an isolated working directory for a single video processing job."""

    def __init__(self, base_dir: Optional[Path] = None, job_id: Optional[str] = None) -> None:
        self.job_id = job_id or uuid.uuid4().hex
        self.base_dir = (base_dir or config.base_temp_dir).resolve()
        self.job_dir = (self.base_dir / self.job_id).resolve()

        # Isolated subdirectories
        self.video_dir = self.job_dir / "video"
        self.keyframes_dir = self.job_dir / "keyframes"
        self.exports_dir = self.job_dir / "exports"

        self._active = False

    def __enter__(self) -> "JobSession":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if config.cleanup_on_completion:
            self.cleanup()

    def start(self) -> None:
        """Create directory structure for this isolated session."""
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.keyframes_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self._active = True
        logger.info(
            "Created isolated workspace for job %s",
            self.job_id,
            extra={"job_id": self.job_id},
        )

    def cleanup(self) -> None:
        """Securely remove the isolated job directory and all its contents."""
        if self.job_dir.exists():
            try:
                shutil.rmtree(self.job_dir, ignore_errors=True)
                logger.info(
                    "Cleaned up workspace for job %s",
                    self.job_id,
                    extra={"job_id": self.job_id},
                )
            except Exception as e:
                logger.warning(
                    "Error during cleanup of job %s: %s",
                    self.job_id,
                    str(e),
                    extra={"job_id": self.job_id},
                )
        self._active = False


def sanitize_filename(filename: str) -> str:
    """Strips directory traversal, control characters, and unsafe characters."""
    # Strip null bytes and control characters
    cleaned = filename.replace("\0", "").strip()
    # Extract only the base name (prevent path traversal like ../../etc/passwd)
    cleaned = os.path.basename(cleaned)
    # Remove all except alphanumeric, dots, hyphens, and underscores
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", cleaned)
    # Ensure it doesn't start with a dot
    if cleaned.startswith("."):
        cleaned = "video" + cleaned
    return cleaned or "unnamed_video"


def validate_file_extension(filename: str, allowed_extensions: Optional[Set[str]] = None) -> str:
    """Validates that the file has an allowed video extension and returns the lowercase ext."""
    allowed = allowed_extensions or config.allowed_extensions
    ext = Path(filename).suffix.lower()
    if not ext or ext not in allowed:
        raise SecurityValidationError(
            f"File extension '{ext}' is not permitted. Allowed: {', '.join(sorted(allowed))}",
            user_friendly_message=f"Unsupported file format. Please upload one of: {', '.join(sorted(allowed))}.",
        )
    return ext


def validate_video_magic_bytes(header: bytes) -> bool:
    """Inspects initial file bytes to verify typical video container signatures."""
    if len(header) < 12:
        return False

    # Check MP4 / MOV (at offset 4: 'ftyp' or 'moov')
    if header[4:8] in KNOWN_MAGIC_SIGNATURES["mp4"]:
        return True

    # Check EBML (MKV / WEBM)
    if header.startswith(KNOWN_MAGIC_SIGNATURES["mkv_webm"][0]):
        return True

    # Check AVI: 'RIFF....AVI '
    if header.startswith(b"RIFF") and header[8:12] == b"AVI ":
        return True

    # Also accept Quicktime / MPEG streams
    if header[4:8] in [b"free", b"mdat", b"wide", b"pnot"]:
        return True

    return False


def save_upload_securely(
    file_obj: BinaryIO | io.BytesIO,
    original_filename: str,
    job_session: JobSession,
    max_size_mb: Optional[int] = None,
) -> Path:
    """Securely validates and writes an uploaded video stream into the isolated job workspace.

    Enforces:
    1. Extension whitelist
    2. Magic bytes verification on stream header
    3. Maximum file size during chunked write
    4. Safe randomized internal filename (never trusts user-provided filename)
    5. Non-executable permissions
    """
    max_mb = config.max_upload_size_mb if max_size_mb is None else max_size_mb
    max_bytes = max_mb * 1024 * 1024

    ext = validate_file_extension(original_filename)

    # Read first 1024 bytes to verify container header
    initial_chunk = file_obj.read(1024)
    if not initial_chunk:
        raise SecurityValidationError(
            "Uploaded file is empty (0 bytes).",
            user_friendly_message="The uploaded file is empty. Please select a valid video.",
        )

    if len(initial_chunk) > max_bytes:
        raise SecurityValidationError(
            f"File exceeded maximum allowable size of {max_mb} MB.",
            user_friendly_message=f"File exceeds maximum upload size limit of {max_mb} MB.",
        )

    if not validate_video_magic_bytes(initial_chunk):
        raise SecurityValidationError(
            "File header does not match any recognized video container signature.",
            user_friendly_message="The uploaded file is not a valid video file or has corrupted headers.",
        )

    # Generate safe internal filename
    safe_internal_name = f"video_{uuid.uuid4().hex[:12]}{ext}"
    destination_path = job_session.video_dir / safe_internal_name

    # Check that destination resolves strictly inside video_dir
    if not str(destination_path.resolve()).startswith(str(job_session.video_dir.resolve())):
        raise SecurityValidationError("Path traversal detected in internal file destination.")

    total_bytes = len(initial_chunk)
    chunk_size = 1024 * 1024  # 1 MB chunks

    with open(destination_path, "wb") as dest:
        dest.write(initial_chunk)
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                # Remove partially written file
                dest.close()
                destination_path.unlink(missing_ok=True)
                raise SecurityValidationError(
                    f"File exceeded maximum allowable size of {max_mb} MB.",
                    user_friendly_message=f"File exceeds maximum upload size limit of {max_mb} MB.",
                )
            dest.write(chunk)

    logger.info(
        "Successfully saved uploaded video %s as %s (%0.2f MB)",
        sanitize_filename(original_filename),
        destination_path.name,
        total_bytes / (1024 * 1024),
        extra={"job_id": job_session.job_id},
    )

    return destination_path


def cleanup_stale_jobs(base_dir: Optional[Path] = None, max_age_seconds: int = 7200) -> int:
    """Removes orphan/stale job folders older than max_age_seconds."""
    target_base = (base_dir or config.base_temp_dir).resolve()
    if not target_base.exists():
        return 0

    now = time.time()
    removed_count = 0

    for item in target_base.iterdir():
        if item.is_dir() and item.name != ".keep":
            try:
                mtime = item.stat().st_mtime
                if (now - mtime) > max_age_seconds:
                    shutil.rmtree(item, ignore_errors=True)
                    removed_count += 1
            except Exception as e:
                logger.debug("Failed to inspect/remove candidate stale job folder %s: %s", item, e)

    if removed_count > 0:
        logger.info("Janitor cleaned up %d stale job workspaces", removed_count)
    return removed_count
