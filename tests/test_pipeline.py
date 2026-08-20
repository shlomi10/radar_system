"""End-to-end tests for the parse → validate → report pipeline."""

from __future__ import annotations

from pathlib import Path

import allure

from main import run
from radar.models import ParseError, RadarPacket
from radar.radar_log_parser import iter_stream

pytestmark = [
    allure.epic("Radar Stream Validator"),
    allure.feature("Pipeline"),
]


@allure.story("Sample stream")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Sample log reports TARGETS, LATENCY, STATE, and parse errors")
def test_sample_stream_reports_expected_failures(
    config_file: Path, tmp_path: Path
) -> None:
    stream = tmp_path / "radar_stream.log"
    stream.write_text(
        "\n".join(
            [
                "10:00:00.100 | PACKET_ID:1001 | STATE:INIT | TARGETS:0 | PAYLOAD:0000000000000000",
                "10:00:00.200 | PACKET_ID:1002 | STATE:SCANNING | TARGETS:0 | PAYLOAD:0000000000000000",
                "10:00:00.320 | PACKET_ID:1003 | STATE:TRACKING | TARGETS:2 | PAYLOAD:000003E8000000FA",
                "10:00:00.400 | PACKET_ID:1004 | STATE:TRACKING | TARGETS:7 | PAYLOAD:000007D00000012C",
                "10:00:00.580 | PACKET_ID:1005 | STATE:SCANNING | TARGETS:0 | PAYLOAD:0000000000000000",
                "10:00:00.650 | PACKET_ID:1006 | STATE:INVALID_STATE | TARGETS:1 | PAYLOAD:000001F400000064",
                "INVALID_CORRUPTED_LINE_WITHOUT_FORMAT",
                "10:00:00.900 | PACKET_ID:1007 | STATE:TRACKING | TARGETS:1 | PAYLOAD:FFFFFFFF00000000",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.txt"

    result = run(str(config_file), str(stream), str(output))
    report = output.read_text(encoding="utf-8")
    allure.attach(report, name="radar-report.txt", attachment_type=allure.attachment_type.TEXT)
    items = list(iter_stream(stream))

    assert sum(isinstance(item, RadarPacket) for item in items) == 7
    assert sum(isinstance(item, ParseError) for item in items) == 1
    assert result.packets_parsed == 7
    assert result.packets_passed == 3
    assert result.overall == "FAIL"
    assert "[PASS] Line 1 | PACKET_ID 1001" in report
    assert "[FAIL] Line 4 | PACKET_ID 1004" in report
    assert "TARGETS: TARGETS 7 exceeds max_allowed_targets 5" in report
    assert "[FAIL] Line 5 | PACKET_ID 1005" in report
    assert "LATENCY: Latency 180ms from PACKET_ID 1004 exceeds max_latency_ms 150" in report
    assert "[FAIL] Line 6 | PACKET_ID 1006" in report
    assert "STATE: STATE 'INVALID_STATE'" in report
    assert "[FAIL] Line 7 | PARSE |" in report
    assert "[FAIL] Line 8 | PACKET_ID 1007" in report
    assert "LATENCY: Latency 250ms from PACKET_ID 1006 exceeds max_latency_ms 150" in report
    assert "WHAT FAILED" not in report
    assert "OVERALL RESULT: FAIL" in report


@allure.story("Clean stream")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("A clean stream reports OVERALL PASS")
def test_clean_stream_reports_overall_pass(config_file: Path, tmp_path: Path) -> None:
    stream = tmp_path / "radar_stream.log"
    stream.write_text(
        "\n".join(
            [
                "10:00:00.100 | PACKET_ID:1001 | STATE:INIT | TARGETS:0 | PAYLOAD:0000000000000000",
                "10:00:00.200 | PACKET_ID:1002 | STATE:SCANNING | TARGETS:0 | PAYLOAD:0000000000000000",
                "10:00:00.320 | PACKET_ID:1003 | STATE:TRACKING | TARGETS:2 | PAYLOAD:E8030000FA000000",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.txt"

    result = run(str(config_file), str(stream), str(output))
    report = output.read_text(encoding="utf-8")
    allure.attach(report, name="radar-report.txt", attachment_type=allure.attachment_type.TEXT)

    assert result.packets_parsed == 3
    assert result.packets_passed == 3
    assert result.overall == "PASS"
    assert "OVERALL RESULT: PASS" in report


@allure.story("Parse error latency")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("A parse error does not replace the previous packet for latency")
def test_parse_error_does_not_reset_latency_previous(
    config_file: Path, tmp_path: Path
) -> None:
    stream = tmp_path / "radar_stream.log"
    stream.write_text(
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
    output = tmp_path / "report.txt"

    result = run(str(config_file), str(stream), str(output))
    report = output.read_text(encoding="utf-8")

    assert result.parse_error_count == 1
    assert "PACKET_ID 1002: LATENCY" not in report
    assert result.packets_passed == 2


@allure.story("Sample stream")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Shipped config.json and radar_stream.log produce the expected FAIL")
def test_shipped_sample_files(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "report.txt"

    result = run(
        str(root / "config" / "config.json"),
        str(root / "data" / "radar_stream.log"),
        str(output),
    )

    assert result.overall == "FAIL"
    assert result.packets_parsed == 7
    assert result.parse_error_count == 1
