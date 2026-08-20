from __future__ import annotations

import json
from pathlib import Path

import pytest

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
