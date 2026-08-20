"""Shared pytest fixtures and Allure test-log capture.

Provides sample_config / config_file and attaches logger output to every test.
"""

from __future__ import annotations

import io
import json
import logging
from pathlib import Path

import allure
import pytest

from radar.logger import LOG_FORMAT, PARENT, get_logger
from radar.models import RadarConfig


@pytest.fixture
def sample_config() -> RadarConfig:
    return RadarConfig(
        system_mode="AIR_TO_AIR",
        max_allowed_targets=5,
        max_latency_ms=150,
        allowed_states=("INIT", "SCANNING", "TRACKING", "ERROR"),
    )


@pytest.fixture
def config_file(tmp_path: Path, sample_config: RadarConfig) -> Path:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "system_mode": sample_config.system_mode,
                "max_allowed_targets": sample_config.max_allowed_targets,
                "max_latency_ms": sample_config.max_latency_ms,
                "allowed_states": list(sample_config.allowed_states),
            }
        ),
        encoding="utf-8",
    )
    return path


@pytest.fixture(autouse=True)
def attach_logs_to_allure(request):
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    parent = logging.getLogger(PARENT)
    parent.addHandler(handler)
    logger = get_logger("tests")
    logger.info("START %s", request.node.nodeid)
    yield
    logger.info("END %s", request.node.nodeid)
    parent.removeHandler(handler)
    handler.close()
    body = buffer.getvalue().strip() or "(no logs)"
    allure.attach(body, name="test-log", attachment_type=allure.attachment_type.TEXT)
