"""Enforce packet rules from the loaded configuration.

Checks allowed STATE, TARGETS limits (including INIT/SCANNING must be 0),
and latency against the previous successfully parsed packet.
"""

from __future__ import annotations

from datetime import datetime

from radar.models import RadarConfig, RadarPacket, Violation

ZERO_TARGETS_STATES = frozenset({"INIT", "SCANNING"})
MS_PER_DAY = 24 * 60 * 60 * 1000


def validate_packet(packet: RadarPacket, previous: RadarPacket | None, config: RadarConfig,) -> list[Violation]:
    violations = _check_state(packet, config)
    violations.extend(_check_targets(packet, config))
    if previous is not None:
        violations.extend(_check_latency(packet, previous, config))
    return violations


def _check_state(packet: RadarPacket, config: RadarConfig) -> list[Violation]:
    if packet.state in config.allowed_states:
        return []
    return [
        Violation(
            packet_id=packet.packet_id,
            line_number=packet.line_number,
            rule="STATE",
            message=(
                f"STATE '{packet.state}' is not in allowed_states "
                f"{list[str](config.allowed_states)}"
            ),
        )
    ]


def _check_targets(packet: RadarPacket, config: RadarConfig) -> list[Violation]:
    violations: list[Violation] = []

    if packet.targets > config.max_allowed_targets:
        violations.append(
            Violation(
                packet_id=packet.packet_id,
                line_number=packet.line_number,
                rule="TARGETS",
                message=(
                    f"TARGETS {packet.targets} exceeds max_allowed_targets "
                    f"{config.max_allowed_targets}"
                ),
            )
        )

    if packet.state in ZERO_TARGETS_STATES and packet.targets != 0:
        violations.append(
            Violation(
                packet_id=packet.packet_id,
                line_number=packet.line_number,
                rule="TARGETS",
                message=(
                    f"STATE '{packet.state}' requires TARGETS to be 0, "
                    f"got {packet.targets}"
                ),
            )
        )

    return violations


def _check_latency(
    packet: RadarPacket,
    previous: RadarPacket,
    config: RadarConfig,
) -> list[Violation]:
    latency_ms = _latency_ms(previous.timestamp, packet.timestamp)
    if latency_ms <= config.max_latency_ms:
        return []
    return [
        Violation(
            packet_id=packet.packet_id,
            line_number=packet.line_number,
            rule="LATENCY",
            message=(
                f"Latency {latency_ms}ms from PACKET_ID {previous.packet_id} "
                f"exceeds max_latency_ms {config.max_latency_ms}"
            ),
        )
    ]


def _latency_ms(previous: datetime, current: datetime) -> int:
    delta = current - previous
    milliseconds = int(delta.total_seconds() * 1000)
    if milliseconds < 0:
        milliseconds += MS_PER_DAY
    return milliseconds
