"""Decode an 8-byte hex payload into unsigned little-endian integers.

The first 4 bytes are distance and the last 4 bytes are velocity.
"""

from __future__ import annotations

PAYLOAD_BYTE_LENGTH = 8
PAYLOAD_HEX_LENGTH = PAYLOAD_BYTE_LENGTH * 2
UINT32_BYTE_LENGTH = 4


def decode_payload(payload_hex: str) -> tuple[int, int]:
    normalized = payload_hex.strip().upper()
    if len(normalized) != PAYLOAD_HEX_LENGTH:
        raise ValueError(
            f"PAYLOAD must be {PAYLOAD_HEX_LENGTH} hex characters "
            f"({PAYLOAD_BYTE_LENGTH} bytes), got {len(normalized)}"
        )
    try:
        raw = bytes.fromhex(normalized)
    except ValueError as exc:
        raise ValueError("PAYLOAD is not a valid hexadecimal string") from exc

    distance = int.from_bytes(raw[:UINT32_BYTE_LENGTH], byteorder="little", signed=False)
    velocity = int.from_bytes(raw[UINT32_BYTE_LENGTH:], byteorder="little", signed=False)
    return distance, velocity
