"""Structured logging configuration for ClipMind AI."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, MutableMapping


class JobContextFilter(logging.Filter):
    """Injects job_id into log records if not already set."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "job_id"):
            record.job_id = "system"
        return True


def setup_logger(name: str = "clipmind", log_level: str | None = None) -> logging.Logger:
    """Configures and returns a structured logger."""
    level_name = log_level or os.getenv("CLIPMIND_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(job_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(JobContextFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logger()
