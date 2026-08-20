"""File and console logging for the radar validator and pytest.

Writes reports/logs/automation.log. Child loggers attach under radar_system
so each Allure test can capture its own test-log.
"""

from __future__ import annotations

import logging
from pathlib import Path

PARENT = "radar_system"
LOG_DIR = Path("reports/logs")
LOG_FILE = LOG_DIR / "automation.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _ensure_configured() -> None:
    parent = logging.getLogger(PARENT)
    parent.setLevel(logging.INFO)
    if parent.handlers:
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    parent.addHandler(file_handler)
    parent.addHandler(console_handler)
    parent.propagate = False


def get_logger(name: str) -> logging.Logger:
    _ensure_configured()
    if name == PARENT or name.startswith(f"{PARENT}."):
        return logging.getLogger(name)
    return logging.getLogger(f"{PARENT}.{name}")
