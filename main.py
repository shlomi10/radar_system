"""CLI entry point for the radar stream validator.

Accepts --config, --stream, and optional --output. Report files are written
under reports/ by default.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from radar.validation_pipeline import run_validation

REPORTS_DIR = Path("reports")
RADAR_REPORTS_DIR = REPORTS_DIR / "radar"
DEFAULT_REPORT = RADAR_REPORTS_DIR / "report.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a radar data stream against a JSON configuration."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to config JSON, for example config/config.json",
    )
    parser.add_argument(
        "--stream",
        required=True,
        help="Path to radar stream log, for example data/radar_stream.log",
    )
    parser.add_argument(
        "--output",
        nargs="?",
        const=str(DEFAULT_REPORT),
        default=None,
        metavar="PATH",
        help=f"Write the report to a file. Default: {DEFAULT_REPORT.as_posix()}",
    )
    return parser.parse_args(argv)


def resolve_output_path(output_path: str | None) -> str | None:
    if output_path is None:
        return None
    destination = Path(output_path)
    if not destination.is_absolute() and destination.parent == Path("."):
        destination = RADAR_REPORTS_DIR / destination.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    return str(destination)


def run(config_path: str, stream_path: str, output_path: str | None = None):
    return run_validation(config_path, stream_path, resolve_output_path(output_path))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run(args.config, args.stream, args.output)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
