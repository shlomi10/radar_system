from __future__ import annotations

import json
import sys
import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = Path(__file__).resolve().parent
STATIC_DIR = UI_DIR / "static"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.runner import run_console

HOST = "127.0.0.1"
PORT = 8765
DEFAULT_CONFIG = ROOT / "config" / "config.json"
DEFAULT_STREAM = ROOT / "data" / "radar_stream.log"
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".json": "application/json; charset=utf-8",
}


def _inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def _resolve_user_path(raw: str) -> Path:
    candidate = Path(raw)
    path = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    if not _inside_root(path):
        raise ValueError("Path must stay inside the project folder")
    return path


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path
        if route in {"/", "/index.html"}:
            self._send_file(STATIC_DIR / "index.html")
            return
        if route == "/api/defaults":
            self._send_json(
                {
                    "config_path": "config/config.json",
                    "stream_path": "data/radar_stream.log",
                }
            )
            return
        if route.startswith("/static/"):
            name = Path(route.removeprefix("/static/")).name
            target = STATIC_DIR / name
            if not target.is_file():
                self._send_status(404, "Not found")
                return
            self._send_file(target)
            return
        if route.startswith("/assets/"):
            name = Path(route.removeprefix("/assets/")).name
            target = ROOT / "assets" / name
            if not target.is_file():
                self._send_status(404, "Not found")
                return
            self._send_file(target)
            return
        self._send_status(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/run":
            self._send_status(404, "Not found")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            result = self._run(payload)
        except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as extra:
            self._send_json({"error": str(extra)}, status=400)
            return
        self._send_json(result)

    def _run(self, payload: dict) -> dict:
        config_text = payload.get("config_text")
        stream_text = payload.get("stream_text")
        if config_text is not None or stream_text is not None:
            if not isinstance(config_text, str) or not isinstance(stream_text, str):
                raise ValueError("config_text and stream_text are required together")
            with tempfile.TemporaryDirectory(prefix="radar-ui-") as folder:
                config_file = Path(folder) / "config.json"
                stream_file = Path(folder) / "radar_stream.log"
                config_file.write_text(config_text, encoding="utf-8")
                stream_file.write_text(stream_text, encoding="utf-8")
                return run_console(str(config_file), str(stream_file))

        config_path = _resolve_user_path(payload.get("config_path") or str(DEFAULT_CONFIG))
        stream_path = _resolve_user_path(payload.get("stream_path") or str(DEFAULT_STREAM))
        return run_console(str(config_path), str(stream_path))

    def _send_file(self, path: Path) -> None:
        data = path.read_bytes()
        content_type = MIME.get(path.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_status(self, status: int, message: str) -> None:
        data = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Radar console: {url}")
    try:
        webbrowser.open(url)
    except OSError:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
        server.server_close()


if __name__ == "__main__":
    main()
