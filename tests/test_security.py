"""Unit tests for upload validation, path traversal prevention, and security checks."""

import io
from pathlib import Path
import pytest

from clipmind.exceptions import SecurityValidationError
from clipmind.security import (
    JobSession,
    sanitize_filename,
    validate_file_extension,
    validate_video_magic_bytes,
    save_upload_securely,
)


def test_sanitize_filename_prevents_traversal():
    """Verify that sanitize_filename strips path traversal sequences."""
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("safe_video.mp4") == "safe_video.mp4"
    assert sanitize_filename("spaced name & weird (chars).mp4") == "spaced_name___weird__chars_.mp4"
    assert sanitize_filename(".hidden_video.mp4") == "video.hidden_video.mp4"


def test_validate_file_extension():
    """Verify whitelist validation for video file extensions."""
    assert validate_file_extension("test.mp4") == ".mp4"
    assert validate_file_extension("clip.MOV") == ".mov"
    assert validate_file_extension("video.mkv") == ".mkv"

    with pytest.raises(SecurityValidationError) as exc:
        validate_file_extension("malware.exe")
    assert "not permitted" in str(exc.value)

    with pytest.raises(SecurityValidationError):
        validate_file_extension("script.sh")

    with pytest.raises(SecurityValidationError):
        validate_file_extension("no_extension_file")


def test_validate_video_magic_bytes():
    """Verify detection of valid and invalid container header signatures."""
    # Fake MP4 header with 'ftyp' at offset 4
    mp4_header = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00"
    assert validate_video_magic_bytes(mp4_header) is True

    # Fake MKV header (EBML signature)
    mkv_header = b"\x1a\x45\xdf\xa3\x93\x42\x82\x88matroska"
    assert validate_video_magic_bytes(mkv_header) is True

    # Fake AVI header: RIFF....AVI
    avi_header = b"RIFF\x24\x00\x00\x00AVI LIST\x00"
    assert validate_video_magic_bytes(avi_header) is True

    # Plain text file or garbage
    assert validate_video_magic_bytes(b"HELLO_WORLD_TEXT_FILE") is False
    assert validate_video_magic_bytes(b"") is False
    assert validate_video_magic_bytes(b"\x00\x00\x00") is False


def test_save_upload_securely(valid_mp4_bytes, tmp_path):
    """Verify stream saving with size and signature enforcement."""
    session = JobSession(base_dir=tmp_path)
    session.start()

    stream = io.BytesIO(valid_mp4_bytes)
    saved_path = save_upload_securely(
        file_obj=stream,
        original_filename="user_upload.mp4",
        job_session=session,
        max_size_mb=10,
    )

    assert saved_path.exists()
    assert saved_path.parent == session.video_dir
    # Filename should be randomized and not equal to raw input
    assert saved_path.name != "user_upload.mp4"
    assert saved_path.suffix == ".mp4"

    session.cleanup()


def test_save_upload_rejects_empty_file(tmp_path):
    """Verify rejection of empty 0-byte upload."""
    session = JobSession(base_dir=tmp_path)
    session.start()

    empty_stream = io.BytesIO(b"")
    with pytest.raises(SecurityValidationError) as exc:
        save_upload_securely(empty_stream, "empty.mp4", session)

    assert "empty" in str(exc.value).lower()
    session.cleanup()


def test_save_upload_rejects_oversized_file(valid_mp4_bytes, tmp_path):
    """Verify rejection when file exceeds configured size limit."""
    session = JobSession(base_dir=tmp_path)
    session.start()

    # Create stream larger than 0.001 MB limit
    stream = io.BytesIO(valid_mp4_bytes * 50)
    with pytest.raises(SecurityValidationError) as exc:
        # Pass 0 MB limit to trigger immediately
        save_upload_securely(stream, "large.mp4", session, max_size_mb=0)

    assert "exceeded maximum allowable size" in str(exc.value)
    session.cleanup()
