"""Stream a live validation report to stdout and optionally to a file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO

from radar.logger import get_logger
from radar.models import ParseError, RadarConfig, RadarPacket, Violation

logger = get_logger(__name__)


@dataclass
class RunResult:
    packets_parsed: int
    packets_passed: int
    violation_count: int
    parse_error_count: int
    overall: str


class ReportWriter:
    def __init__(self, streams: list[TextIO]) -> None:
        self._streams = streams
        self.packets_parsed = 0
        self.packets_passed = 0
        self.violation_count = 0
        self.parse_error_count = 0

    def write_header(self, config: RadarConfig) -> None:
        self._emit("=" * 64)
        self._emit("RADAR STREAM VALIDATION REPORT")
        self._emit("=" * 64)
        self._emit(f"System mode: {config.system_mode}")
        self._emit(f"Max allowed targets: {config.max_allowed_targets}")
        self._emit(f"Max latency (ms): {config.max_latency_ms}")
        self._emit(f"Allowed states: {list(config.allowed_states)}")
        self._emit("")
        self._emit("LIVE RESULTS")
        self._emit("-" * 64)

    def write_packet(self, packet: RadarPacket) -> None:
        self.packets_parsed += 1
        self._emit(
            f"PACKET_ID {packet.packet_id} | {packet.timestamp.strftime('%H:%M:%S.%f')[:-3]} | "
            f"STATE={packet.state} | TARGETS={packet.targets} | "
            f"DISTANCE={packet.distance} | VELOCITY={packet.velocity}"
        )

    def write_parse_error(self, error: ParseError) -> None:
        self.parse_error_count += 1
        self._emit(
            f"Line {error.line_number}: PARSE error - {error.reason} "
            f"(raw: {error.raw_line})"
        )

    def write_violations(self, violations: list[Violation]) -> None:
        if not violations:
            self.packets_passed += 1
            return
        self.violation_count += len(violations)
        for violation in violations:
            packet_label = (
                f"PACKET_ID {violation.packet_id}"
                if violation.packet_id is not None
                else f"Line {violation.line_number}"
            )
            self._emit(f"{packet_label}: {violation.rule} - {violation.message}")

    def write_footer(self) -> RunResult:
        overall = "PASS" if self.violation_count == 0 and self.parse_error_count == 0 else "FAIL"
        self._emit("")
        self._emit("=" * 64)
        self._emit(f"Packets processed successfully: {self.packets_parsed}")
        self._emit(f"Packets that passed all rules: {self.packets_passed}")
        self._emit(f"Rule violations: {self.violation_count}")
        self._emit(f"Parse errors: {self.parse_error_count}")
        self._emit(f"OVERALL RESULT: {overall}")
        self._emit("=" * 64)
        logger.info("OVERALL RESULT: %s", overall)
        return RunResult(
            packets_parsed=self.packets_parsed,
            packets_passed=self.packets_passed,
            violation_count=self.violation_count,
            parse_error_count=self.parse_error_count,
            overall=overall,
        )

    def _emit(self, line: str) -> None:
        text = line + "\n"
        for stream in self._streams:
            stream.write(text)
            stream.flush()
