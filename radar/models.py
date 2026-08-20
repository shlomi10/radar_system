"""Shared data models for config, packets, parse errors, and rule violations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RadarConfig:
    system_mode: str
    max_allowed_targets: int
    max_latency_ms: int
    allowed_states: tuple[str, ...]


@dataclass(frozen=True)
class RadarPacket:
    line_number: int
    timestamp: datetime
    packet_id: int
    state: str
    targets: int
    payload_hex: str
    distance: int
    velocity: int


@dataclass(frozen=True)
class ParseError:
    line_number: int
    raw_line: str
    reason: str


@dataclass(frozen=True)
class Violation:
    packet_id: int | None
    line_number: int
    rule: str
    message: str
