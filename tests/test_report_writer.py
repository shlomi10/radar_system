from __future__ import annotations

from io import StringIO

import allure

from radar.models import ParseError, Violation
from radar.report_writer import ReportWriter
from tests.helpers import make_packet

pytestmark = [
    allure.epic("Radar Stream Validator"),
    allure.feature("Report"),
]


@allure.story("PASS")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("A packet with no violations counts as PASS")
def test_report_writer_pass(sample_config) -> None:
    buffer = StringIO()
    writer = ReportWriter([buffer])
    writer.write_header(sample_config)
    writer.write_packet(make_packet(state="INIT", targets=0))
    writer.write_violations([])
    result = writer.write_footer()

    text = buffer.getvalue()
    allure.attach(text, name="radar-report.txt", attachment_type=allure.attachment_type.TEXT)

    assert result.overall == "PASS"
    assert result.packets_parsed == 1
    assert result.packets_passed == 1
    assert "OVERALL RESULT: PASS" in text
    assert "AIR_TO_AIR" in text


@allure.story("FAIL")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Rule violations and parse errors make the overall result FAIL")
def test_report_writer_fail(sample_config) -> None:
    buffer = StringIO()
    writer = ReportWriter([buffer])
    writer.write_header(sample_config)
    writer.write_packet(make_packet(packet_id=1004, targets=7))
    writer.write_violations(
        [
            Violation(
                packet_id=1004,
                line_number=4,
                rule="TARGETS",
                message="TARGETS 7 exceeds max_allowed_targets 5",
            )
        ]
    )
    writer.write_parse_error(
        ParseError(line_number=7, raw_line="BAD", reason="Line does not match expected packet format")
    )
    result = writer.write_footer()

    text = buffer.getvalue()
    allure.attach(text, name="radar-report.txt", attachment_type=allure.attachment_type.TEXT)

    assert result.overall == "FAIL"
    assert result.violation_count == 1
    assert result.parse_error_count == 1
    assert result.packets_passed == 0
    assert "PACKET_ID 1004: TARGETS" in text
    assert "PARSE error" in text
    assert "OVERALL RESULT: FAIL" in text
