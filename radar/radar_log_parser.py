"""Parse radar log lines into packets without loading the whole file.

iter_stream() reads the file object line by line. A corrupted line becomes a
ParseError and the rest of the stream continues.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from radar.models import ParseError, RadarPacket
from radar.payload_decoder import decode_payload

FIELD_SEPARATOR = "|"
KEY_VALUE_SEPARATOR = ":"
REQUIRED_FIELDS = ("PACKET_ID", "STATE", "TARGETS", "PAYLOAD")


def iter_stream(path: str | Path) -> Iterator[RadarPacket | ParseError]:
    stream_path = Path(path)
    if not stream_path.is_file():
        raise FileNotFoundError(f"Radar stream file not found: {stream_path}")

    with stream_path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                yield parse_line(line, line_number)
            except ValueError as exc:
                yield ParseError(
                    line_number=line_number,
                    raw_line=line,
                    reason=str(exc),
                )


def parse_line(line: str, line_number: int) -> RadarPacket:
    parts = [part.strip() for part in line.split(FIELD_SEPARATOR)]
    if len(parts) != 5:
        raise ValueError("Line does not match expected packet format")

    timestamp = _parse_timestamp(parts[0])
    fields = _parse_key_value_fields(parts[1:])

    missing = [name for name in REQUIRED_FIELDS if name not in fields]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")

    packet_id = _parse_int(fields["PACKET_ID"], "PACKET_ID")
    targets = _parse_int(fields["TARGETS"], "TARGETS")
    if targets < 0:
        raise ValueError("TARGETS must be >= 0")

    state = fields["STATE"]
    if not state:
        raise ValueError("STATE is empty")

    payload_hex = fields["PAYLOAD"].upper()
    distance, velocity = decode_payload(payload_hex)

    return RadarPacket(
        line_number=line_number,
        timestamp=timestamp,
        packet_id=packet_id,
        state=state,
        targets=targets,
        payload_hex=payload_hex,
        distance=distance,
        velocity=velocity,
    )


def _parse_timestamp(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%H:%M:%S.%f")
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp: {value}") from exc


def _parse_key_value_fields(parts: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in parts:
        if KEY_VALUE_SEPARATOR not in part:
            raise ValueError(f"Invalid field: {part}")
        key, value = part.split(KEY_VALUE_SEPARATOR, maxsplit=1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError("Empty field name")
        if key in fields:
            raise ValueError(f"Duplicate field: {key}")
        fields[key] = value
    return fields


def _parse_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} is not an integer: {value}") from exc
