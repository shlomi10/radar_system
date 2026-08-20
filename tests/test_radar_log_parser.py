"""Tests for line-by-line stream parsing and corrupted-line handling."""

from __future__ import annotations

import inspect
from pathlib import Path

import allure
import pytest

from radar.models import ParseError
from radar.radar_log_parser import iter_stream, parse_line
from radar import radar_log_parser

pytestmark = [
    allure.epic("Radar Stream Validator"),
    allure.feature("Parser"),
]


@allure.story("Parse line")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("A valid log line is split into packet fields")
def test_parse_line_extracts_fields() -> None:
    packet = parse_line(
        "10:00:00.320 | PACKET_ID:1003 | STATE:TRACKING | TARGETS:2 | PAYLOAD:000003E8000000FA",
        line_number=3,
    )

    assert packet.packet_id == 1003
    assert packet.state == "TRACKING"
    assert packet.targets == 2
    assert packet.distance == 3892510720
    assert packet.velocity == 4194304000


@allure.story("Corrupted line")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("A corrupted line does not stop the stream")
def test_iter_stream_continues_after_corrupted_line(tmp_path: Path) -> None:
    path = tmp_path / "radar_stream.log"
    path.write_text(
        "\n".join(
            [
                "10:00:00.100 | PACKET_ID:1001 | STATE:INIT | TARGETS:0 | PAYLOAD:0000000000000000",
                "INVALID_CORRUPTED_LINE_WITHOUT_FORMAT",
                "10:00:00.200 | PACKET_ID:1002 | STATE:SCANNING | TARGETS:0 | PAYLOAD:0000000000000000",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    packets = []
    errors = []
    for item in iter_stream(path):
        if isinstance(item, ParseError):
            errors.append(item)
        else:
            packets.append(item)

    assert [packet.packet_id for packet in packets] == [1001, 1002]
    assert len(errors) == 1
    assert errors[0].line_number == 2


@allure.story("Streaming read")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Parser does not load the whole file with readlines")
def test_parser_does_not_use_readlines() -> None:
    source = inspect.getsource(radar_log_parser)
    assert "readlines(" not in source
    assert "read_text(" not in source


@allure.story("Parse line")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Lowercase PAYLOAD is normalized to uppercase")
def test_parse_line_normalizes_payload_hex() -> None:
    packet = parse_line(
        "10:00:00.320 | PACKET_ID:1003 | STATE:TRACKING | TARGETS:2 | PAYLOAD:e8030000fa000000",
        line_number=1,
    )

    assert packet.payload_hex == "E8030000FA000000"
    assert packet.distance == 1000
    assert packet.velocity == 250


@allure.story("Blank lines")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Blank lines are skipped")
def test_iter_stream_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "radar_stream.log"
    path.write_text(
        "10:00:00.100 | PACKET_ID:1001 | STATE:INIT | TARGETS:0 | PAYLOAD:0000000000000000\n"
        "\n"
        "   \n"
        "10:00:00.200 | PACKET_ID:1002 | STATE:SCANNING | TARGETS:0 | PAYLOAD:0000000000000000\n",
        encoding="utf-8",
    )

    items = list(iter_stream(path))
    assert [item.packet_id for item in items] == [1001, 1002]


@allure.story("Missing file")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Missing stream file raises FileNotFoundError")
def test_iter_stream_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        list(iter_stream(tmp_path / "missing.log"))


@allure.story("Corrupted line")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Invalid timestamp, empty STATE, and negative TARGETS become parse errors")
@pytest.mark.parametrize(
    "line, reason",
    [
        (
            "not-a-time | PACKET_ID:1 | STATE:INIT | TARGETS:0 | PAYLOAD:0000000000000000",
            "Invalid timestamp",
        ),
        (
            "10:00:00.100 | PACKET_ID:1 | STATE: | TARGETS:0 | PAYLOAD:0000000000000000",
            "STATE is empty",
        ),
        (
            "10:00:00.100 | PACKET_ID:1 | STATE:INIT | TARGETS:-1 | PAYLOAD:0000000000000000",
            "TARGETS must be >= 0",
        ),
        (
            "10:00:00.100 | PACKET_ID:abc | STATE:INIT | TARGETS:0 | PAYLOAD:0000000000000000",
            "PACKET_ID is not an integer",
        ),
        (
            "10:00:00.100 | PACKET_ID:1 | STATE:INIT | TARGETS:0",
            "Line does not match expected packet format",
        ),
    ],
)
def test_parse_line_rejects_invalid_fields(line: str, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        parse_line(line, line_number=1)
