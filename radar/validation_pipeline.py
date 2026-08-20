"""Run the parse → validate → report pipeline with constant memory.

Only the previous packet is kept, so the stream can be large.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

from radar.config_reader import load_config
from radar.models import ParseError
from radar.packet_validator import validate_packet
from radar.radar_log_parser import iter_stream
from radar.report_writer import ReportWriter, RunResult


def run_validation(
    config_path: str,
    stream_path: str, output_path: str | None = None, stdout: TextIO | None = None,
) -> RunResult:
    config = load_config(config_path)
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

        return writer.write_footer()
    finally:
        if output_file is not None:
            output_file.close()
