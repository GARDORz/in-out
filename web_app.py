"""Local attendance web server with persistent JSON event storage."""
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from src.attendance import clock_in, clock_out, monthly_report

ROOT = Path(__file__).resolve().parent
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


class EventStore:
    def __init__(self, path):
        self.path = Path(path)
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.events = [
                {"type": item["type"], "emp": item["emp"],
                 "ts": datetime.fromisoformat(item["ts"])}
                for item in raw
            ]
        else:
            self.events = []

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {"type": item["type"], "emp": item["emp"],
             "ts": item["ts"].isoformat(timespec="minutes")}
            for item in self.events
        ]
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        os.replace(temporary, self.path)


def make_handler(data_path):
    store = EventStore(data_path)

    class Handler(BaseHTTPRequestHandler):
        def send_json(self, data, status=200):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path in STATIC:
                filename, content_type = STATIC[parsed.path]
                body = (ROOT / "web" / filename).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/api/events":
                self.send_json([
                    {"type": event["type"], "emp": event["emp"],
                     "ts": event["ts"].isoformat(timespec="minutes")}
                    for event in reversed(store.events[-20:])
                ])
                return
            if parsed.path == "/api/report":
                try:
                    params = parse_qs(parsed.query)
                    year = int(params["year"][0])
                    month = int(params["month"][0])
                    if not 1 <= month <= 12:
                        raise ValueError("month must be 1 through 12")
                except (KeyError, IndexError, ValueError) as exc:
                    self.send_json({"error": str(exc)}, 400)
                    return
                self.send_json(monthly_report(store.events, year, month))
                return
            self.send_json({"error": "Not found"}, 404)

        def do_POST(self):
            if self.path not in ("/api/clock-in", "/api/clock-out"):
                self.send_json({"error": "Not found"}, 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 4096:
                    raise ValueError("Invalid request size")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("Expected a JSON object")
                if not isinstance(payload.get("emp"), str) or not isinstance(payload.get("ts"), str):
                    raise ValueError("Employee ID and timestamp must be strings")
                emp = payload["emp"].strip()
                if not emp or len(emp) > 60:
                    raise ValueError("Employee ID must be 1–60 characters")
                ts = datetime.fromisoformat(payload["ts"])
                if ts.tzinfo is not None:
                    raise ValueError("Use local time without a timezone")
                if self.path == "/api/clock-in":
                    clock_in(store.events, emp, ts)
                else:
                    clock_out(store.events, emp, ts)
                store.save()
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                self.send_json({"error": str(exc)}, 400)
                return
            self.send_json(
                {"type": store.events[-1]["type"], "emp": emp,
                 "ts": ts.isoformat(timespec="minutes")}, 201
            )

    return Handler


def main():
    data_path = Path(os.environ.get("ATTENDANCE_DATA", ROOT / "data" / "events.json"))
    port = int(os.environ.get("ATTENDANCE_PORT", "8000"))
    server = HTTPServer(("127.0.0.1", port), make_handler(data_path))
    print(f"Attendance web app: http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
