import json
import threading
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from web_app import EventStore, make_handler


@pytest.fixture
def app(tmp_path):
    path = tmp_path / "events.json"
    server = HTTPServer(("127.0.0.1", 0), make_handler(path))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port), path
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def get_json(url):
    with urlopen(url) as response:
        return json.load(response)


def post_json(url, payload):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.load(response)


def test_page_and_api_work_together(app):
    base, path = app
    with urlopen(base + "/") as response:
        page = response.read().decode("utf-8")
        assert response.status == 200
        assert "ระบบเข้า-ออกงาน" in page
    with urlopen(base + "/app.js") as response:
        assert b"submitAction" in response.read()

    payload = {"emp": "emp-001", "ts": "2026-11-03T09:15"}
    assert post_json(base + "/api/clock-in", payload)[0] == 201
    assert post_json(
        base + "/api/clock-out",
        {"emp": "emp-001", "ts": "2026-11-03T19:15"},
    )[0] == 201
    report = get_json(base + "/api/report?year=2026&month=11")
    assert report["emp-001"] == {
        "days": 1,
        "total_hours": 10.0,
        "late_days": 1,
        "overtime_hours": 2.0,
    }
    assert len(get_json(base + "/api/events")) == 2
    assert len(EventStore(path).events) == 2


def test_invalid_transition_returns_400_and_does_not_persist(app):
    base, path = app
    payload = {"emp": "emp-001", "ts": "2026-11-03T09:00"}
    post_json(base + "/api/clock-in", payload)
    with pytest.raises(HTTPError) as duplicate:
        post_json(base + "/api/clock-in", payload)
    assert duplicate.value.code == 400
    assert len(EventStore(path).events) == 1
