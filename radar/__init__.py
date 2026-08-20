"""Radar stream validation package.

Loads runtime configuration, parses a hardware log stream line by line,
decodes hex payloads, enforces STATE / TARGETS / latency rules, and prints
a live summary report.
"""

from radar.config_reader import load_config
from radar.payload_decoder import decode_payload
from radar.packet_validator import validate_packet
from radar.radar_log_parser import iter_stream
from radar.validation_pipeline import run_validation

__all__ = [
    "load_config",
    "iter_stream",
    "decode_payload",
    "validate_packet",
    "run_validation",
]
