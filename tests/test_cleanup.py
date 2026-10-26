"""Unit tests for temporary file lifecycle and cleanup janitor."""

import time
from pathlib import Path

from clipmind.security import JobSession, cleanup_stale_jobs


def test_job_session_cleanup(tmp_path: Path):
    """Verify JobSession creates and cleanly removes temporary files."""
    session = JobSession(base_dir=tmp_path)
    session.start()

    assert session.job_dir.exists()
    assert session.video_dir.exists()

    # Create dummy file inside
    dummy = session.video_dir / "test.txt"
    dummy.write_text("temporary data")
    assert dummy.exists()

    session.cleanup()
    assert not session.job_dir.exists()


def test_job_session_context_manager(tmp_path: Path):
    """Verify context manager automatically triggers cleanup on exit."""
    with JobSession(base_dir=tmp_path) as session:
        job_dir = session.job_dir
        assert job_dir.exists()

    # After exiting block
    assert not job_dir.exists()


def test_cleanup_stale_jobs(tmp_path: Path):
    """Verify janitor identifies and removes old job directories."""
    base_dir = tmp_path / "janitor_test"
    base_dir.mkdir(parents=True)

    old_job = base_dir / "old_job_123"
    old_job.mkdir()
    (old_job / "dummy.txt").write_text("old")

    # Call cleanup with 0 seconds max_age to target all existing directories
    removed = cleanup_stale_jobs(base_dir=base_dir, max_age_seconds=0)
    assert removed == 1
    assert not old_job.exists()
