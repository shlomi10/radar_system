from __future__ import annotations

import allure
import pytest

from radar.payload_decoder import decode_payload

pytestmark = [
    allure.epic("Radar Stream Validator"),
    allure.feature("Payload"),
]


@allure.story("Unsigned little-endian decode")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("PAYLOAD hex decodes to Distance and Velocity")
@pytest.mark.parametrize(
    "payload, distance, velocity",
    [
        ("0000000000000000", 0, 0),
        ("000003E8000000FA", 3892510720, 4194304000),
        ("E8030000FA000000", 1000, 250),
        ("FFFFFFFF00000000", 4294967295, 0),
        ("00000000FFFFFFFF", 0, 4294967295),
    ],
)
def test_decode_payload_unsigned_little_endian(
    payload: str, distance: int, velocity: int
) -> None:
    assert decode_payload(payload) == (distance, velocity)


@allure.story("Invalid payload")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Invalid PAYLOAD values are rejected")
@pytest.mark.parametrize("payload", ["000003E8", "ZZZZZZZZ00000000", ""])
def test_decode_payload_rejects_invalid_values(payload: str) -> None:
    with pytest.raises(ValueError, match="PAYLOAD"):
        decode_payload(payload)


@allure.story("Unsigned little-endian decode")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Lowercase hex and surrounding whitespace are accepted")
def test_decode_payload_accepts_lowercase_and_whitespace() -> None:
    assert decode_payload("  e8030000fa000000  ") == (1000, 250)
