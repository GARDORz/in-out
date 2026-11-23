# in-out

A small Python attendance app with a local web interface and a repeatable performance baseline.

## Run the web app

Use Python 3.12 or newer. From the repository root:

```powershell
python web_app.py
```

Open **http://127.0.0.1:8000** in a browser. Enter an employee ID and local date/time, then choose **เข้างาน** (clock in) or **ออกงาน** (clock out). Select a year and month to view days worked, total hours, late days, and overtime. Events are saved to `data/events.json` and survive a restart. The server listens only on your computer.

To use a different data file or port, set `ATTENDANCE_DATA` or `ATTENDANCE_PORT` before starting the server.

## Tests and benchmark

```powershell
python -m pip install pytest
python -m pytest -q
python bench.py
```

See `TEST_RESULTS.md` for the latest verified test and benchmark output. The fixed baseline and optimization target are in `GOALS.md`; experiment rules are in `RULES.md`. This repository is a local demo without authentication and is not intended for an internet-facing deployment.
