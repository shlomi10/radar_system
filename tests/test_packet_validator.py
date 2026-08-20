"""Tests for STATE, TARGETS, and Latency rule enforcement."""

from __future__ import annotations

import allure

from radar.models import RadarConfig
from radar.packet_validator import validate_packet
from tests.helpers import make_packet

pytestmark = [
    allure.epic("Radar Stream Validator"),
    allure.feature("Validator"),
]


@allure.story("STATE")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("STATE outside allowed_states is reported")
def test_invalid_state_is_reported(sample_config: RadarConfig) -> None:
    packet = make_packet(state="INVALID_STATE", packet_id=1006)

    violations = validate_packet(packet, None, sample_config)

    assert len(violations) == 1
    assert violations[0].rule == "STATE"
    assert violations[0].packet_id == 1006


@allure.story("TARGETS")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("TARGETS above the maximum is reported")
def test_targets_cannot_exceed_maximum(sample_config: RadarConfig) -> None:
    packet = make_packet(targets=7, packet_id=1004)

    violations = validate_packet(packet, None, sample_config)

    assert len(violations) == 1
    assert violations[0].rule == "TARGETS"


@allure.story("TARGETS")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("INIT and SCANNING require TARGETS=0")
def test_init_and_scanning_require_zero_targets(sample_config: RadarConfig) -> None:
    init_violations = validate_packet(
        make_packet(state="INIT", targets=1, packet_id=1010), None, sample_config
    )
    scanning_violations = validate_packet(
        make_packet(state="SCANNING", targets=2, packet_id=1011), None, sample_config
    )

    assert init_violations[0].rule == "TARGETS"
    assert scanning_violations[0].rule == "TARGETS"


@allure.story("LATENCY")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("The first packet is not checked for latency")
def test_first_packet_has_no_latency_check(sample_config: RadarConfig) -> None:
    packet = make_packet(state="INIT", targets=0)

    assert validate_packet(packet, None, sample_config) == []


@allure.story("LATENCY")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Latency above max_latency_ms is reported")
def test_latency_above_max_is_reported(sample_config: RadarConfig) -> None:
    previous = make_packet(
        timestamp="10:00:00.400", packet_id=1004, state="TRACKING", targets=1
    )
    current = make_packet(
        timestamp="10:00:00.580", packet_id=1005, state="SCANNING", targets=0
    )

    violations = validate_packet(current, previous, sample_config)

    assert len(violations) == 1
    assert violations[0].rule == "LATENCY"
    assert "180ms" in violations[0].message
    assert violations[0].packet_id == 1005


@allure.story("LATENCY")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Latency equal to max_latency_ms is allowed")
def test_latency_equal_to_max_is_allowed(sample_config: RadarConfig) -> None:
    previous = make_packet(timestamp="10:00:00.000", packet_id=1, state="TRACKING", targets=1)
    current = make_packet(timestamp="10:00:00.150", packet_id=2, state="TRACKING", targets=1)

    assert validate_packet(current, previous, sample_config) == []


@allure.story("LATENCY")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Midnight wrap-around is handled for latency")
def test_latency_handles_midnight_wrap(sample_config: RadarConfig) -> None:
    previous = make_packet(
        timestamp="23:59:59.900", packet_id=1, state="TRACKING", targets=1
    )
    within = make_packet(
        timestamp="00:00:00.050", packet_id=2, state="TRACKING", targets=1
    )
    over = make_packet(
        timestamp="00:00:00.200", packet_id=3, state="TRACKING", targets=1
    )

    assert validate_packet(within, previous, sample_config) == []
    violations = validate_packet(over, previous, sample_config)
    assert len(violations) == 1
    assert violations[0].rule == "LATENCY"


@allure.story("STATE")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Allowed TRACKING and ERROR packets pass")
def test_allowed_states_pass(sample_config: RadarConfig) -> None:
    tracking = make_packet(state="TRACKING", targets=5, packet_id=1)
    error = make_packet(state="ERROR", targets=0, packet_id=2)

    assert validate_packet(tracking, None, sample_config) == []
    assert validate_packet(error, None, sample_config) == []


@allure.story("STATE")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Invalid STATE and TARGETS can fail on the same packet")
def test_multiple_violations_on_one_packet(sample_config: RadarConfig) -> None:
    packet = make_packet(state="INVALID_STATE", targets=9, packet_id=99)

    violations = validate_packet(packet, None, sample_config)
    rules = [violation.rule for violation in violations]

    assert "STATE" in rules
    assert "TARGETS" in rules
