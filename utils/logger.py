"""
Logging configuration — dual output: rotating file + console.

Import and use:
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("ETL completed")
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.config import LOG_DIR, LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL

_LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _setup_root_logger() -> None:
    """Configure the root logger once."""
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "shopee_bi.log"

    level = _LOG_LEVEL_MAP.get(LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on re-import
    if not root.handlers:
        root.addHandler(file_handler)
        root.addHandler(console_handler)


_setup_root_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a named logger child of the pre-configured root."""
    return logging.getLogger(name)
