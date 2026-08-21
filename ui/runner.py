from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from radar.config_reader import load_config
from radar.models import ParseError, RadarPacket
from radar.packet_validator import validate_packet
from radar.radar_log_parser import iter_stream

MAX_EVENTS = 5000


def run_console(config_path: str, stream_path: str) -> dict:
    config = load_config(config_path)
    events: list[dict] = []
    previous = None
    packets_parsed = 0
    packets_passed = 0
    violation_count = 0
    parse_error_count = 0
    truncated = False

    for item in iter_stream(stream_path):
        if len(events) >= MAX_EVENTS:
            truncated = True
            break
        if isinstance(item, ParseError):
            parse_error_count += 1
            events.append(
                {
                    "kind": "parse",
                    "status": "FAIL",
                    "line_number": item.line_number,
                    "packet_id": None,
                    "timestamp": None,
                    "state": None,
                    "targets": None,
                    "distance": None,
                    "velocity": None,
                    "payload_hex": None,
                    "rules": ["PARSE"],
                    "reasons": [item.reason],
                    "raw": item.raw_line,
                }
            )
            continue

        packets_parsed += 1
        violations = validate_packet(item, previous, config)
        previous = item
        if violations:
            violation_count += len(violations)
            status = "FAIL"
            rules = [violation.rule for violation in violations]
            reasons = [violation.message for violation in violations]
        else:
            packets_passed += 1
            status = "PASS"
            rules = []
            reasons = []
        events.append(_packet_event(item, status, rules, reasons))

    overall = "PASS" if violation_count == 0 and parse_error_count == 0 else "FAIL"
    return {
        "config": {
            "system_mode": config.system_mode,
            "max_allowed_targets": config.max_allowed_targets,
            "max_latency_ms": config.max_latency_ms,
            "allowed_states": list(config.allowed_states),
        },
        "counters": {
            "packets_parsed": packets_parsed,
            "packets_passed": packets_passed,
            "packets_failed": packets_parsed - packets_passed,
            "violation_count": violation_count,
            "parse_error_count": parse_error_count,
            "overall": overall,
        },
        "events": events,
        "truncated": truncated,
    }


def _packet_event(
    packet: RadarPacket, status: str, rules: list[str], reasons: list[str]
) -> dict:
    return {
        "kind": "packet",
        "status": status,
        "line_number": packet.line_number,
        "packet_id": packet.packet_id,
        "timestamp": packet.timestamp.strftime("%H:%M:%S.%f")[:-3],
        "state": packet.state,
        "targets": packet.targets,
        "distance": packet.distance,
        "velocity": packet.velocity,
        "payload_hex": packet.payload_hex,
        "rules": rules,
        "reasons": reasons,
        "raw": None,
    }
