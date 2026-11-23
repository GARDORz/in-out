# Test Results

## Web app check — 2026-11-23

- Branch: `rsi/1`
- Commit tested: `eece20a56b9c13efb15f86a226382b428696f82d`
- Environment: GitHub Actions `ubuntu-latest`, CPython 3.12.16
- Command: `python -m pytest -q`
- Result: **12 passed in 1.07s**
- Coverage exercised: attendance rules, monthly calculations, HTML/JavaScript delivery, clock-in/out API, monthly report API, rejected duplicate clock-in, and persistence after reopening the event store.
- Command: `python bench.py`
- `time_seconds=0.222804`
- `checksum=0bffe5da318341b1ddf1d91096efa44250743e453bcceb0e09b9e75c2f40799c`
- [Full workflow log](https://github.com/GARDORz/in-out/actions/runs/45112678979): success

The checksum matches the original round-0 baseline. The report implementation and benchmark were not changed for this web feature. Elapsed time varies between shared CI runs; this run is a verification measurement, not an RSI speed result.

## Run locally

From the repository root, run `python web_app.py` and open `http://127.0.0.1:8000`. The web interface requires no extra Python packages. To repeat the checks, install pytest with `python -m pip install pytest`, then run `python -m pytest -q` and `python bench.py`.
