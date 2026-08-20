from __future__ import annotations

from pathlib import Path

import allure

from main import DEFAULT_REPORT, main, parse_args, resolve_output_path

pytestmark = [
    allure.epic("Radar Stream Validator"),
    allure.feature("CLI"),
]


@allure.story("Arguments")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("--config and --stream are required")
def test_parse_args_requires_config_and_stream() -> None:
    args = parse_args(["--config", "config/config.json", "--stream", "data/radar_stream.log"])

    assert args.config == "config/config.json"
    assert args.stream == "data/radar_stream.log"
    assert args.output is None


@allure.story("Arguments")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("--output without a path defaults to reports/radar/report.txt")
def test_parse_args_output_flag_uses_default_report() -> None:
    args = parse_args(
        ["--config", "c.json", "--stream", "s.log", "--output"]
    )

    assert args.output == str(DEFAULT_REPORT)


@allure.story("Output path")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("A bare filename is written under reports/radar/")
def test_resolve_output_bare_filename_goes_under_reports_radar(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    path = resolve_output_path("summary.txt")

    assert Path(path) == Path("reports") / "radar" / "summary.txt"
    assert (tmp_path / "reports" / "radar").is_dir()


@allure.story("Exit code")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Missing files return exit code 1")
def test_main_missing_files_returns_1() -> None:
    assert main(["--config", "missing.json", "--stream", "missing.log"]) == 1


@allure.story("Exit code")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("A valid run returns exit code 0 even when the stream FAILs")
def test_main_valid_run_returns_0(config_file: Path, tmp_path: Path) -> None:
    stream = tmp_path / "radar_stream.log"
    stream.write_text(
        "10:00:00.100 | PACKET_ID:1001 | STATE:INIT | TARGETS:0 | PAYLOAD:0000000000000000\n"
        "10:00:00.400 | PACKET_ID:1004 | STATE:TRACKING | TARGETS:7 | PAYLOAD:0000000000000000\n",
        encoding="utf-8",
    )

    assert main(["--config", str(config_file), "--stream", str(stream)]) == 0
