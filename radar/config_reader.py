"""Load and validate the runtime JSON configuration.

Required keys: system_mode, max_allowed_targets, max_latency_ms, allowed_states.
system_mode must be a non-empty string; its value is not restricted.
"""

from __future__ import annotations

import json
from pathlib import Path

from radar.logger import get_logger
from radar.models import RadarConfig

logger = get_logger(__name__)


def load_config(path: str | Path) -> RadarConfig:
    config_path = Path(path)
    if not config_path.is_file():
        logger.error("Config file not found: %s", config_path)
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in config file: %s", config_path)
        raise ValueError(f"Invalid JSON in config file: {config_path}") from exc

    if not isinstance(raw, dict):
        logger.error("Config root must be a JSON object")
        raise ValueError("Config root must be a JSON object")

    system_mode = _require(raw, "system_mode", str)
    max_allowed_targets = _require(raw, "max_allowed_targets", int)
    max_latency_ms = _require(raw, "max_latency_ms", int)
    allowed_states_raw = _require(raw, "allowed_states", list)

    if max_allowed_targets < 0:
        raise ValueError("max_allowed_targets must be >= 0")
    if max_latency_ms < 0:
        raise ValueError("max_latency_ms must be >= 0")
    if not system_mode.strip():
        raise ValueError("system_mode must be a non-empty string")
    if not allowed_states_raw:
        raise ValueError("allowed_states must contain at least one state")
    if any(not isinstance(state, str) or not state.strip() for state in allowed_states_raw):
        raise ValueError("allowed_states must contain non-empty strings only")

    config = RadarConfig(
        system_mode=system_mode,
        max_allowed_targets=max_allowed_targets,
        max_latency_ms=max_latency_ms,
        allowed_states=tuple[str, ...](allowed_states_raw),
    )
    logger.info(
        "Loaded config from %s | mode=%s max_targets=%s max_latency_ms=%s states=%s",
        config_path,
        config.system_mode,
        config.max_allowed_targets,
        config.max_latency_ms,
        list(config.allowed_states),
    )
    return config


def _require(raw: dict, key: str, expected_type: type):
    if key not in raw:
        logger.error("Missing required config key: %s", key)
        raise ValueError(f"Missing required config key: {key}")
    value = raw[key]
    if expected_type is int and isinstance(value, bool):
        logger.error("Config key '%s' must be of type %s", key, expected_type.__name__)
        raise ValueError(f"Config key '{key}' must be of type {expected_type.__name__}")
    if not isinstance(value, expected_type):
        logger.error("Config key '%s' must be of type %s", key, expected_type.__name__)
        raise ValueError(f"Config key '{key}' must be of type {expected_type.__name__}")
    return value
