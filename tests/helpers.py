"""Packet factory for unit tests that do not parse a real log line."""

from __future__ import annotations

from datetime import datetime

from radar.models import RadarPacket


def make_packet(
    *,
    line_number: int = 1,
    timestamp: str = "10:00:00.100",
    packet_id: int = 1001,
    state: str = "TRACKING",
    targets: int = 1,
    payload_hex: str = "000003E8000000FA",
    distance: int = 3892510720,
    velocity: int = 4194304000,
) -> RadarPacket:
    return RadarPacket(
        line_number=line_number,
        timestamp=datetime.strptime(timestamp, "%H:%M:%S.%f"),
        packet_id=packet_id,
        state=state,
        targets=targets,
        payload_hex=payload_hex,
        distance=distance,
        velocity=velocity,
    )
