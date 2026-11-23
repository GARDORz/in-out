# Repository Guidelines

## Project Structure & Module Organization

`src/attendance.py` holds the attendance calculations. `web_app.py` serves the browser interface and JSON API; `web/` contains its HTML, CSS, and JavaScript. Runtime events are stored in ignored `data/events.json`. `tests/test_attendance.py` checks attendance rules; `tests/test_web_app.py` checks HTTP behavior and persistence. `bench.py` generates fixed-seed data for 400 employees across 22 days and prints elapsed report time and a SHA-256 checksum. `.github/workflows/baseline.yml` runs the checks on `rsi/*`. Read `GOALS.md`, `RULES.md`, `PROTOCOL.md`, `EXPERIMENTS.md`, and `LESSONS.md` before an experiment.

## Build, Test, and Development Commands

Use Python 3.12. Run `python web_app.py` and open `http://127.0.0.1:8000` for the local website. Install the only test dependency with `python -m pip install pytest`. Run `python -m pytest -q` for the full test suite. Run `python bench.py` to measure `monthly_report` and print `time_seconds` plus `checksum`. There is no build step or external service. See `TEST_RESULTS.md` for recorded output.

## Coding Style & Naming Conventions

Use four spaces, standard-library Python where possible, and `snake_case` for modules, functions, and variables. Keep event dictionaries consistent: `{"type": "in", "emp": "e1", "ts": datetime(...)}`. Keep the baseline implementation readable. No formatter or linter is configured; follow PEP 8 and review diffs for accidental formatting churn.

## Testing Guidelines

Pytest is the test framework. Name test functions `test_<behavior>`. Add focused cases for behavior changes, then run the entire suite. For performance experiments, the fixed checksum in `GOALS.md` and passing tests are correctness gates. No coverage percentage is configured.

## Commit & Pull Request Guidelines

The initial history uses short, imperative commit subjects; the measured starting point is committed as `baseline`. Work on branches matching `rsi/<n>`. A PR should state the single hypothesis, changed behavior, test result, benchmark time, checksum, and link to its `EXPERIMENTS.md` row. For RSI optimization rounds, follow `RULES.md`: edit only `src/attendance.py`, `LESSONS.md`, and append-only `EXPERIMENTS.md`. The web feature was separately requested.
