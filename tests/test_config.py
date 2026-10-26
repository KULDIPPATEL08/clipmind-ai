"""Unit tests for configuration management and environment overrides."""

import os
from pathlib import Path

from clipmind.config import AppConfig


def test_default_config_initialization():
    """Test that AppConfig initializes with sensible defaults."""
    cfg = AppConfig()
    assert cfg.app_name == "ClipMind AI"
    assert cfg.max_upload_size_mb == 500
    assert cfg.max_video_duration_seconds == 3600
    assert ".mp4" in cfg.allowed_extensions
    assert ".mov" in cfg.allowed_extensions
    assert cfg.default_detector == "content"
    assert cfg.default_content_threshold == 27.0
    assert cfg.default_min_scene_length_frames == 15
    assert cfg.base_temp_dir.exists()


def test_config_env_overrides(monkeypatch, tmp_path):
    """Test that environment variables correctly override configuration."""
    custom_temp = tmp_path / "custom_tmp"
    monkeypatch.setenv("CLIPMIND_DEBUG", "true")
    monkeypatch.setenv("CLIPMIND_MAX_UPLOAD_MB", "100")
    monkeypatch.setenv("CLIPMIND_MAX_DURATION_SEC", "1200")
    monkeypatch.setenv("CLIPMIND_TEMP_DIR", str(custom_temp))
    monkeypatch.setenv("CLIPMIND_AUTO_CLEANUP", "false")

    cfg = AppConfig()
    assert cfg.debug is True
    assert cfg.max_upload_size_mb == 100
    assert cfg.max_video_duration_seconds == 1200
    assert cfg.base_temp_dir == custom_temp.resolve()
    assert cfg.cleanup_on_completion is False
    assert custom_temp.exists()
