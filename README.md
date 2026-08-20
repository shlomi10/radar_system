![Radar Stream Validator](assets/radar-banner.png)

# 📡 Radar Stream Validator

Catch bad radar packets in a live stream — parse, decode, enforce, report.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/pytest-56%20tests-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest">
  <img src="https://img.shields.io/badge/Allure-Test%20Reports-FF6A00?style=for-the-badge&logo=allure&logoColor=white" alt="Allure">
  <a href="https://shlomi10.github.io/radar_system/"><img src="https://img.shields.io/badge/%E2%96%B6%20Live%20Allure-7C3AED?style=for-the-badge&logo=githubpages&logoColor=white" alt="Live Allure"></a>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Runtime-stdlib%20only-10B981?style=for-the-badge&logo=python&logoColor=white" alt="stdlib">
  <img src="https://img.shields.io/badge/CLI-argparse-8B5CF6?style=for-the-badge&logo=windowsterminal&logoColor=white" alt="CLI">
  <img src="https://img.shields.io/badge/Domain-Radar%20Automation-DC2626?style=for-the-badge&logo=target&logoColor=white" alt="Radar">
  <img src="https://img.shields.io/badge/Streaming-O(1)%20memory-F59E0B?style=for-the-badge&logo=apachekafka&logoColor=white" alt="Streaming">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/GitHub%20Actions-CI%20%2B%20Pages-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="Actions">
  <img src="https://img.shields.io/badge/venv-isolated%20env-FACC15?style=for-the-badge&logo=python&logoColor=black" alt="venv">
  <img src="https://img.shields.io/badge/Logging-automation.log-EC4899?style=for-the-badge&logo=datadog&logoColor=white" alt="Logging">
  <img src="https://img.shields.io/badge/Docker-optional-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Report-PASS%20%2F%20FAIL-14B8A6?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Report">
</p>

A CLI automation tool that loads `config.json`, reads a radar hardware log **line by line**, decodes an 8-byte hex `PAYLOAD` (unsigned little-endian Distance + Velocity), and enforces STATE / TARGETS / Latency rules while printing a live summary.

📦 Repo: [github.com/shlomi10/radar_system](https://github.com/shlomi10/radar_system)  
📊 Live Allure: [shlomi10.github.io/radar_system](https://shlomi10.github.io/radar_system/)

---

## 📌 Overview

```text
config.json  +  radar_stream.log  →  parse  →  decode  →  enforce  →  live report
```

What you get:

- 🖥️ CLI validator (`main.py`) — `--config`, `--stream`, `--output`
- 🧩 Modular runtime under `radar/` — **stdlib only**
- 🧪 56 pytest tests with Allure epic / feature / story / severity
- 📝 Logger to `reports/logs/automation.log` — also attached to every Allure test
- 🚀 GitHub Actions → Allure on GitHub Pages + radar report artifact
- 🐳 Optional Docker image — validator + pytest without a local venv

---

## 🏗️ Architecture

Constant-memory pipeline: one previous packet for latency, four integer counters, no `readlines()`, no packet list, no failure list.

Runtime, tests, and Allure all sit on the same `radar/` package:

```mermaid
flowchart TB
    subgraph IN["📥 Inputs"]
        CFG["⚙️ config.json"]
        LOG["📜 radar_stream.log"]
    end

    subgraph CORE["🧩 radar/"]
        LOAD["config_reader"]
        PARSE["radar_log_parser"]
        PAY["payload_decoder"]
        VAL["packet_validator"]
        PIPE["validation_pipeline"]
        REP["report_writer"]
        LG["logger"]
    end

    subgraph RUNTIME["🖥️ CLI"]
        MAIN["main.py<br/>argparse"]
    end

    subgraph TESTS["🧪 tests/  ·  pytest + Allure"]
        PYT["python -m pytest"]
        CONF["conftest.py<br/>Allure labels + test-log"]
        SUITE["56 tests<br/>config · payload · parser<br/>validator · pipeline · report · CLI"]
    end

    subgraph OUT["📤 Outputs"]
        LIVE["📺 Live radar report"]
        FILE["📁 reports/radar/report.txt"]
        ALOG["📒 reports/logs/automation.log"]
        ARES["📊 reports/allure-results"]
        PAGES["🌐 GitHub Pages Allure"]
    end

    CFG --> MAIN
    LOG --> MAIN
    MAIN --> PIPE
    PIPE --> LOAD
    LOAD --> PARSE
    PARSE --> PAY
    PAY --> VAL
    VAL --> REP
    PIPE --> LG
    REP --> LIVE
    REP --> FILE
    LG --> ALOG

    PYT --> CONF
    CONF --> SUITE
    SUITE --> CORE
    SUITE --> ARES
    ARES --> PAGES
```

pytest → Allure → GitHub Pages:

```mermaid
flowchart LR
    T["🧪 pytest<br/>56 tests"] --> L["Allure annotations<br/>epic · feature · story · severity"]
    T --> LOGS["test-log attached<br/>to every test"]
    T --> R["reports/allure-results"]
    R --> G["allure generate"]
    G --> H["reports/allure-report"]
    H --> CI["GitHub Actions<br/>on main"]
    CI --> P["shlomi10.github.io/radar_system"]
```

Packet path inside the stream:

```mermaid
flowchart LR
    L["Line n"] --> Q{Format OK?}
    Q -->|no| E["ParseError<br/>continue"]
    Q -->|yes| P["RadarPacket"]
    P --> D["Distance + Velocity"]
    D --> R{Rules}
    R -->|pass| OK["✅ count++"]
    R -->|fail| BAD["❌ STATE / TARGETS / LATENCY"]
    E --> N["Next line"]
    OK --> N
    BAD --> N
```

---

## 🧱 Project structure

```text
radar-validator/
├── .github/workflows/ci.yml
├── radar/
│   ├── config_reader.py
│   ├── models.py
│   ├── radar_log_parser.py
│   ├── payload_decoder.py
│   ├── packet_validator.py
│   ├── report_writer.py
│   ├── validation_pipeline.py
│   └── logger.py
├── tests/
├── config/config.json
├── data/radar_stream.log
├── assets/radar-banner.png
├── main.py
├── pytest.ini
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

| File | Responsibility |
| --- | --- |
| `radar/config_reader.py` | Load and validate `config.json` |
| `radar/models.py` | Shared data models |
| `radar/radar_log_parser.py` | Line-by-line log parsing |
| `radar/payload_decoder.py` | Unsigned little-endian Distance and Velocity |
| `radar/packet_validator.py` | Enforce STATE, TARGETS, and Latency rules |
| `radar/report_writer.py` | Live report: write each result immediately, keep counters only |
| `radar/validation_pipeline.py` | Constant-memory pipeline: previous packet + counters |
| `radar/logger.py` | File and console logging |
| `main.py` | CLI entry point and runtime arguments |
| `tests/` | pytest + Allure — config, payload, parser, validator, pipeline, report, CLI |
| `.github/workflows/ci.yml` | pytest, Allure, radar report, GitHub Pages |
| `Dockerfile` | Python 3.14-slim image: install deps, run `main.py` by default |
| `.dockerignore` | Keep `.venv`, `.git`, `reports/`, and caches out of the image |

---

## 🛠 Tech stack

| Layer | Tools |
| --- | --- |
| Runtime | Python 3.14+ stdlib (`argparse`, `json`, `pathlib`, `datetime`, `logging`) |
| Tests | pytest · allure-pytest |
| CI | GitHub Actions · GitHub Pages |
| Container | Docker |

---

## 🧾 Logging

```text
reports/logs/automation.log
```

`radar/logger.py` is used by config, payload, parser, validator, pipeline, report, and CLI.

Every pytest test attaches its captured log to Allure as **`test-log`**.

---

## ✅ Prerequisites

- Python 3.14+
- Git
- Docker Desktop (daemon running) only if you want to run the image
- Node.js / npm and Java only if you want to open Allure HTML locally

---

## 📦 Installation

```bash
python -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the validator

- `--config` — JSON rules, for example `config/config.json`
- `--stream` — log file, for example `data/radar_stream.log`
- `--output` — writes under `reports/radar/` (default `reports/radar/report.txt`) and still prints to the screen

```bash
python main.py --config config/config.json --stream data/radar_stream.log
python main.py --config config/config.json --stream data/radar_stream.log --output
python main.py --config config/config.json --stream data/radar_stream.log --output summary.txt
```

---

## 🐳 Docker

The image is `python:3.14-slim`. It installs `requirements.txt`, copies `config/`, `data/`, `radar/`, `tests/`, `main.py`, and `pytest.ini`, then runs the validator.

Default command:

```text
python main.py --config config/config.json --stream data/radar_stream.log
```

Start Docker Desktop first. If the daemon is off, `docker build` fails with a pipe / engine error.

Build:

```bash
docker build -t radar-system .
```

Validate the sample stream (stdout only):

```bash
docker run --rm radar-system
```

Write the report (and logs) to `reports/` on the host:

```powershell
docker run --rm -v ${PWD}/reports:/app/reports radar-system --config config/config.json --stream data/radar_stream.log --output
```

Same idea in bash / Git Bash:

```bash
docker run --rm -v "$PWD/reports:/app/reports" radar-system --config config/config.json --stream data/radar_stream.log --output
```

`--output` still prints to the screen. The file lands at `reports/radar/report.txt`. Extra args after the image name replace the default `CMD`.

Run pytest inside the image:

```bash
docker run --rm --entrypoint python radar-system -m pytest -v
```

---

## 🧪 Running tests

pytest is the automation framework. Runtime validation still uses the standard library only.

```bash
python -m pytest
python -m pytest -v
python -m pytest tests/test_packet_validator.py
python -m pytest tests/test_pipeline.py
```

56 tests. Full titles live in Allure: [shlomi10.github.io/radar_system](https://shlomi10.github.io/radar_system/)

| File | Tests | What they cover |
| --- | ---: | --- |
| `tests/test_config_reader.py` | 16 | Load `config.json`; any non-empty `system_mode`; missing keys; wrong types; empty / blank `allowed_states` |
| `tests/test_payload_decoder.py` | 9 | Unsigned little-endian Distance + Velocity; sample hex; invalid length / non-hex |
| `tests/test_radar_log_parser.py` | 11 | Field split; corrupted line does not stop the stream; no `readlines()`; blank lines; bad timestamp / STATE / TARGETS / PACKET_ID |
| `tests/test_packet_validator.py` | 9 | STATE, TARGETS, INIT/SCANNING=0, first-packet latency skip, max latency, midnight wrap, multiple violations |
| `tests/test_pipeline.py` | 4 | Sample log FAIL (TARGETS, LATENCY, STATE, parse); clean stream PASS; parse error does not reset latency; shipped files |
| `tests/test_report_writer.py` | 2 | `[PASS]` / `[FAIL]` live report and counters |
| `tests/test_cli.py` | 5 | Required args; `--output` path; missing files exit 1; stream FAIL still exit 0 |

---

## 📊 Allure report

Live CI report — republished on every `main` run:

**https://shlomi10.github.io/radar_system/**

Each test includes a `test-log` attachment.

```bash
python -m pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
allure serve reports/allure-results
```

---

## 📁 Runtime artifacts

Generated at runtime (gitignored):

```text
reports/
├── allure-results/
├── allure-report/
├── pytest/
├── radar/report.txt
└── logs/automation.log
```

---

## 🚀 GitHub Actions

Repo: [https://github.com/shlomi10/radar_system](https://github.com/shlomi10/radar_system)

Push to `main` or **Actions → CI → Run workflow**.

One-time Pages setup: **Settings → Pages → Deploy from a branch → `gh-pages` / root → Save**.

The sample log is expected to finish with `OVERALL RESULT: FAIL` — that is a successful program run, not a CI crash.

How to read the radar report in CI:

- `[PASS]` — this log line parsed and passed every rule
- `[FAIL]` — this log line is the problem (`Line N` is the line number in `radar_stream.log`)
- indented `TARGETS` / `STATE` / `LATENCY` / `PARSE` — why that line failed (printed immediately, not stored)
- `Packets parsed` — how many packets were decoded (not how many passed)
- `OVERALL RESULT: FAIL` — at least one rule violation or parse error

---

## 📡 Large-stream reading

The stream is an iterator over the file object (`for raw_line in handle`). No `readlines()`, no full-file load, no packet list, no accumulated failure list. Memory keeps the previous packet (latency), four counters (`packets_parsed`, `packets_passed`, `violation_count`, `parse_error_count`), and the current line. Failures are written to the report as they happen.

---

## 📄 File formats

`config/config.json`:

- `system_mode` — non-empty string
- `max_allowed_targets` — maximum targets
- `max_latency_ms` — max gap between consecutive parsed packets
- `allowed_states` — legal states

Log line:

```text
HH:MM:SS.mmm | PACKET_ID:<id> | STATE:<state> | TARGETS:<n> | PAYLOAD:<16 hex chars>
```

`PAYLOAD` = 8 bytes hex, unsigned little-endian:

- First 4 bytes → Distance (`uint32` LE)
- Last 4 bytes → Velocity (`uint32` LE)

`bytes.fromhex` + `int.from_bytes(..., "little")`.

---

## 🛡️ Validation rules

1. `STATE` must be in `allowed_states`
2. `TARGETS` must not exceed `max_allowed_targets`
3. `INIT` / `SCANNING` → `TARGETS` must be 0
4. Latency vs the previous **successfully parsed** packet must not exceed `max_latency_ms` (first packet skipped; midnight wrap handled)

A corrupted line is a parse error; the stream continues. Latency is never computed against a failed parse.

---

## 📈 Sample file results

Log file: `data/radar_stream.log`

✅ Passed: Line 1 **1001**, Line 2 **1002**, Line 3 **1003**

❌ Failed:

| Log line | Packet | Why |
| --- | --- | --- |
| 4 | **1004** | `TARGETS=7` exceeds max 5 |
| 5 | **1005** | latency 180ms from 1004 > 150 |
| 6 | **1006** | `INVALID_STATE` not in allowed_states |
| 7 | — | malformed line, no PACKET_ID |
| 8 | **1007** | latency 250ms from 1006 > 150 |

`OVERALL RESULT: FAIL`

Example payload: `000003E8` / `000000FA` → Distance=**3892510720**, Velocity=**4194304000** (unsigned LE).

---

## 🧷 Pytest configuration

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
docker build -t radar-system .
docker run --rm radar-system
docker run --rm -v ${PWD}/reports:/app/reports radar-system --output
docker run --rm --entrypoint python radar-system -m pytest -v
```

---

## ❤️ Made By

Built by **Shlomi** — from code to the world, with love.
