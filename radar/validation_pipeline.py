"""Run the parse → validate → report pipeline with constant memory.

Only the previous packet and report counters are kept, so the stream can be large.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

from radar.config_reader import load_config
from radar.logger import get_logger
from radar.models import ParseError
from radar.packet_validator import validate_packet
from radar.radar_log_parser import iter_stream
from radar.report_writer import ReportWriter, RunResult

logger = get_logger(__name__)


def run_validation(
    config_path: str,
    stream_path: str, output_path: str | None = None, stdout: TextIO | None = None,
) -> RunResult:
    config = load_config(config_path)
    logger.info("Starting validation stream=%s output=%s", stream_path, output_path)
    streams: list[TextIO] = [stdout or sys.stdout]
    output_file: TextIO | None = None

    try:
        if output_path:
            destination = Path(output_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            output_file = destination.open("w", encoding="utf-8")
            streams.append(output_file)

        writer = ReportWriter(streams)
        writer.write_header(config)

        previous = None
        for item in iter_stream(stream_path):
            if isinstance(item, ParseError):
                writer.write_parse_error(item)
                continue
            writer.write_packet(item)
            writer.write_violations(validate_packet(item, previous, config))
            previous = item

        result = writer.write_footer()
        logger.info(
            "Validation finished overall=%s parsed=%s passed=%s violations=%s parse_errors=%s",
            result.overall,
            result.packets_parsed,
            result.packets_passed,
            result.violation_count,
            result.parse_error_count,
        )
        return result
    finally:
        if output_file is not None:
            output_file.close()
