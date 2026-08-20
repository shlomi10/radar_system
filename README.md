![Radar Stream Validator](assets/radar-banner.png)

# 📡 Radar Stream Validator

An automation tool for validating a radar system data stream.

![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-automation%20framework-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Allure](https://img.shields.io/badge/Allure-Test%20Reports-FF6A00?style=for-the-badge&logo=allure&logoColor=white)
![Standard Library](https://img.shields.io/badge/Runtime-stdlib%20only-0EA5E9?style=for-the-badge&logo=python&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-argparse-111827?style=for-the-badge&logo=windowsterminal&logoColor=white)
![Radar Automation](https://img.shields.io/badge/Domain-Radar%20Automation-22C55E?style=for-the-badge&logo=target&logoColor=white)
![Streaming](https://img.shields.io/badge/Streaming-O(1)%20memory-F59E0B?style=for-the-badge&logo=apachekafka&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%20report-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![venv](https://img.shields.io/badge/venv-isolated%20env-FACC15?style=for-the-badge&logo=python&logoColor=black)
[![Allure Report](https://img.shields.io/badge/%E2%96%B6%20Allure%20report-FF6A00?style=for-the-badge)](https://shlomi10.github.io/radar_system/)

The program loads a configuration file, parses radar log packets (including a raw hardware payload), enforces the validation rules, and prints a live summary report while reading.

Repository:

```text
https://github.com/shlomi10/radar_system
```

📊 **Allure report (kept up to date after every CI run on `main`):** [shlomi10.github.io/radar_system](https://shlomi10.github.io/radar_system/)

---

## 📌 Overview

Core flow:

```text
config.json → parse stream → decode PAYLOAD → enforce rules → live report
```

This project includes:

- CLI validator (`main.py`) with `--config`, `--stream`, and `--output`
- Modular runtime under `radar/` (stdlib only)
- pytest suite with Allure annotations
- GitHub Actions that publishes Allure to GitHub Pages, plus pytest and radar reports

---

## 🧱 Project structure

```text
radar-validator/
├── .github/
│   └── workflows/
│       └── ci.yml
├── radar/
│   ├── __init__.py
│   ├── config_reader.py
│   ├── models.py
│   ├── radar_log_parser.py
│   ├── payload_decoder.py
│   ├── packet_validator.py
│   ├── report_writer.py
│   └── validation_pipeline.py
├── tests/
│   ├── conftest.py
│   ├── helpers.py
│   ├── test_config_reader.py
│   ├── test_payload_decoder.py
│   ├── test_radar_log_parser.py
│   ├── test_packet_validator.py
│   ├── test_pipeline.py
│   ├── test_report_writer.py
│   └── test_cli.py
├── config/
│   └── config.json
├── data/
│   └── radar_stream.log
├── assets/
│   └── radar-banner.png
├── reports/
│   ├── allure-results/
│   ├── allure-report/
│   ├── pytest/
│   └── radar/
├── main.py
├── pytest.ini
├── requirements.txt
└── README.md
```

| File | Responsibility |
| --- | --- |
| `radar/config_reader.py` | Load and validate `config.json` |
| `radar/models.py` | Shared data models |
| `radar/radar_log_parser.py` | Line-by-line log parsing |
| `radar/payload_decoder.py` | Unsigned little-endian Distance and Velocity |
| `radar/packet_validator.py` | Enforce STATE, TARGETS, and Latency rules |
| `radar/report_writer.py` | Live report while processing |
| `radar/validation_pipeline.py` | Constant-memory processing pipeline |
| `main.py` | CLI entry point and runtime arguments |
| `tests/conftest.py` | Shared pytest fixtures |
| `tests/helpers.py` | Packet factory for unit tests |
| `tests/test_config_reader.py` | Config loading tests |
| `tests/test_payload_decoder.py` | Payload decode tests |
| `tests/test_radar_log_parser.py` | Stream parsing tests |
| `tests/test_packet_validator.py` | Rule enforcement tests |
| `tests/test_pipeline.py` | End-to-end sample-log test |
| `tests/test_report_writer.py` | Live report PASS/FAIL text |
| `tests/test_cli.py` | argparse, output path, exit codes |
| `pytest.ini` | pytest discovery, `pythonpath`, Allure results dir |
| `requirements.txt` | pytest + allure-pytest |
| `.github/workflows/ci.yml` | GitHub Actions: pytest, Allure, radar report |

---

## 🛠 Tech stack

- Python 3.14+
- pytest
- allure-pytest
- Python standard library for runtime validation (`argparse`, `json`, `pathlib`, `datetime`)

---

## ✅ Prerequisites

Install before running:

- Python 3.14+
- Git
- Node.js / npm and Java only if you want to generate or open Allure HTML locally

---

## 📦 Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the validator

File paths are passed to `main.py` through `argparse`:

- `--config` — path to the JSON file, for example `config/config.json`
- `--stream` — path to the log file, for example `data/radar_stream.log`
- `--output` — writes the radar report under `reports/radar/`. With no filename, it is saved as `reports/radar/report.txt`. The report is also printed to the screen.

```bash
python main.py --config config/config.json --stream data/radar_stream.log
python main.py --config config/config.json --stream data/radar_stream.log --output
python main.py --config config/config.json --stream data/radar_stream.log --output summary.txt
```

---

## 🧪 Running tests

pytest is the automation framework. Runtime validation still uses the Python standard library only.

Run all tests:

```bash
python -m pytest
```

Run with verbose output:

```bash
python -m pytest -v
```

Run a single module:

```bash
python -m pytest tests/test_packet_validator.py
python -m pytest tests/test_pipeline.py
```

The suite covers config loading, unsigned little-endian payload decode, line-by-line parsing (including a corrupted line that must not stop the stream), STATE / TARGETS / Latency rules, and an end-to-end run on the sample log.

---

## 📊 Allure report

Live CI report on GitHub Pages. Every run on `main` republishes it.

**https://shlomi10.github.io/radar_system/**

`pytest.ini` already writes Allure results to `reports/allure-results`.

Generate Allure results:

```bash
python -m pytest --alluredir=reports/allure-results
```

Generate an Allure HTML report:

```bash
allure generate reports/allure-results -o reports/allure-report
```

Open Allure report:

```bash
allure open reports/allure-report
```

Serve Allure without generating a static folder:

```bash
allure serve reports/allure-results
```

---

## 📁 Runtime artifacts

All generated reports land under `reports/`:

```text
reports/
├── allure-results/
├── allure-report/
├── pytest/
│   ├── junit.xml
│   └── output.txt
└── radar/
    └── report.txt
```

| Path | Source |
| --- | --- |
| `reports/allure-results/` | pytest / allure-pytest |
| `reports/allure-report/` | `allure generate` |
| `reports/pytest/` | JUnit XML and pytest console output (CI) |
| `reports/radar/report.txt` | `python main.py --output` |

`reports/` is gitignored.

---

## 🚀 GitHub Actions

Repo: [https://github.com/shlomi10/radar_system](https://github.com/shlomi10/radar_system)

Open **Actions → CI → Run workflow**, or push to `main`.

The run page shows:

- pytest (`-v` output + JUnit XML)
- Allure HTML (published to GitHub Pages)
- radar stream validation (`reports/radar/report.txt`)

When the job finishes on `main`, the Allure HTML report is republished so the live report stays up to date:

**https://shlomi10.github.io/radar_system/**

One-time setup: repo **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `gh-pages` / `/ (root)` → Save**.

You can still download the `reports` artifact from the Actions run. The sample log is expected to finish with `OVERALL RESULT: FAIL`; that is a successful program run, not a CI crash.

---

## 📡 Large-stream reading

The stream is read as an iterator over the file object (`for raw_line in handle`). There is no `readlines()`, the whole file is not loaded into memory, and packets are not collected into a list. Memory keeps only the previous packet (for latency), the summary counters, and the current line. Violations are printed as soon as they are found.

---

## 📄 File formats

`config/config.json` defines the enforcement rules at runtime:

- `system_mode` — system mode (must be a non-empty string)
- `max_allowed_targets` — maximum allowed targets
- `max_latency_ms` — maximum time gap between consecutive parsed packets
- `allowed_states` — list of legal states

A line in `data/radar_stream.log`:

```text
HH:MM:SS.mmm | PACKET_ID:<id> | STATE:<state> | TARGETS:<n> | PAYLOAD:<16 hex chars>
```

`PAYLOAD` is 8 bytes in hex, decoded as unsigned little-endian integers:

- First 4 bytes → Distance (`uint32` LE)
- Last 4 bytes → Velocity (`uint32` LE)

Conversion uses `bytes.fromhex` and `int.from_bytes(..., "little")`.

---

## 🛡️ Validation rules

1. `STATE` must appear in `allowed_states`.
2. `TARGETS` must not exceed `max_allowed_targets`.
3. In `INIT` or `SCANNING`, the target count must be 0.
4. The time gap between the current packet and the previous successfully parsed packet must not exceed `max_latency_ms`. The first packet is not checked for latency. Midnight wrap-around is handled.

A corrupted line is recorded as a parse error and processing continues. Latency is computed only between packets that were parsed successfully.

---

## 📈 Sample file results

Passed: 1001, 1002, 1003.

Failed:

- 1004 — `TARGETS=7` exceeds the maximum of 5
- 1005 — latency 180ms exceeds 150 (from 1004 at 10:00:00.400 to 1005 at 10:00:00.580)
- 1006 — `INVALID_STATE` is not in `allowed_states`
- Line 7 — malformed line, no PACKET_ID
- 1007 — latency 250ms exceeds 150 (from 1006 at 10:00:00.650 to 1007 at 10:00:00.900)

`OVERALL RESULT: FAIL`

Example payload: `000003E8` / `000000FA` → Distance=3892510720, Velocity=4194304000 (unsigned little-endian).

---

## 🧷 Pytest configuration

`pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = tests
addopts = -ra --alluredir=reports/allure-results
```

---

## ✅ Useful commands

```bash
python -m venv .venv
pip install -r requirements.txt
python main.py --config config/config.json --stream data/radar_stream.log --output
python -m pytest -v
python -m pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

---

## ❤️ Made By

Built by **Shlomi** — from code to the world, with love.
