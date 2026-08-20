from __future__ import annotations

import json
from pathlib import Path

import allure
import pytest

from radar.config_reader import load_config


def _write_config(tmp_path: Path, **fields) -> Path:
    payload = {
        "system_mode": "AIR_TO_AIR",
        "max_allowed_targets": 5,
        "max_latency_ms": 150,
        "allowed_states": ["INIT"],
    }
    payload.update(fields)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path

pytestmark = [
    allure.epic("Radar Stream Validator"),
    allure.feature("Config"),
]


@allure.story("Load valid JSON")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Valid config is loaded into RadarConfig")
def test_load_config_reads_valid_file(config_file: Path) -> None:
    config = load_config(config_file)

    assert config.system_mode == "AIR_TO_AIR"
    assert config.max_allowed_targets == 5
    assert config.max_latency_ms == 150
    assert config.allowed_states == ("INIT", "SCANNING", "TRACKING", "ERROR")


@allure.story("system_mode")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Any non-empty system_mode is accepted")
def test_load_config_accepts_any_non_empty_system_mode(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "system_mode": "AIR_TO_GROUND",
                "max_allowed_targets": 5,
                "max_latency_ms": 150,
                "allowed_states": ["INIT"],
            }
        ),
        encoding="utf-8",
    )

    config = load_config(path)
    assert config.system_mode == "AIR_TO_GROUND"


@allure.story("system_mode")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Empty system_mode is rejected")
def test_load_config_rejects_empty_system_mode(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "system_mode": "   ",
                "max_allowed_targets": 5,
                "max_latency_ms": 150,
                "allowed_states": ["INIT"],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="system_mode"):
        load_config(path)


@allure.story("Type checks")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("bool is not accepted as int")
def test_load_config_rejects_bool_as_int(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "system_mode": "AIR_TO_AIR",
                "max_allowed_targets": True,
                "max_latency_ms": 150,
                "allowed_states": ["INIT"],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="max_allowed_targets"):
        load_config(path)


@allure.story("Missing file")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Missing config file raises FileNotFoundError")
def test_load_config_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "missing.json")


@allure.story("Invalid JSON")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Invalid JSON is rejected")
def test_load_config_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_config(path)


@allure.story("Invalid JSON")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Config root must be a JSON object")
def test_load_config_rejects_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON object"):
        load_config(path)


@allure.story("Missing keys")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Missing required keys are rejected")
@pytest.mark.parametrize(
    "key",
    ["system_mode", "max_allowed_targets", "max_latency_ms", "allowed_states"],
)
def test_load_config_rejects_missing_key(tmp_path: Path, key: str) -> None:
    payload = {
        "system_mode": "AIR_TO_AIR",
        "max_allowed_targets": 5,
        "max_latency_ms": 150,
        "allowed_states": ["INIT"],
    }
    del payload[key]
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=key):
        load_config(path)


@allure.story("Type checks")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Wrong value types are rejected")
def test_load_config_rejects_wrong_types(tmp_path: Path) -> None:
    path = _write_config(tmp_path, max_allowed_targets="5")

    with pytest.raises(ValueError, match="max_allowed_targets"):
        load_config(path)


@allure.story("Range checks")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Negative numeric limits are rejected")
@pytest.mark.parametrize("field", ["max_allowed_targets", "max_latency_ms"])
def test_load_config_rejects_negative_limits(tmp_path: Path, field: str) -> None:
    path = _write_config(tmp_path, **{field: -1})

    with pytest.raises(ValueError, match=field):
        load_config(path)


@allure.story("allowed_states")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Empty allowed_states is rejected")
def test_load_config_rejects_empty_allowed_states(tmp_path: Path) -> None:
    path = _write_config(tmp_path, allowed_states=[])

    with pytest.raises(ValueError, match="allowed_states"):
        load_config(path)


@allure.story("allowed_states")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Blank allowed_states entries are rejected")
def test_load_config_rejects_blank_allowed_states(tmp_path: Path) -> None:
    path = _write_config(tmp_path, allowed_states=["INIT", "  "])

    with pytest.raises(ValueError, match="allowed_states"):
        load_config(path)
