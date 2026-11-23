# Goals

Reduce `python bench.py`'s `time_seconds` by at least 10× from the baseline while all tests pass and the checksum stays identical.

## Baseline (round 0)

- Branch: `rsi/0`
- Environment: GitHub Actions `ubuntu-latest`, CPython 3.12.16
- Tests: 10 passed
- `time_seconds`: `0.142108`
- Required target: `0.0142108` seconds or less in a comparable environment
- SHA-256 checksum: `0bffe5da318341b1ddf1d91096efa44250743e453bcceb0e09b9e75c2f40799c`
- Evidence: [baseline workflow run](https://github.com/GARDORz/in-out/actions/runs/45111755969)

Use the same fixed-seed benchmark and comparable runner when judging speed. Correctness and checksum are mandatory.
