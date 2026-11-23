"""Repeatable November 2026 attendance benchmark."""
import hashlib
import json
import random
import time
from datetime import datetime, timedelta

from src.attendance import clock_in, clock_out, monthly_report


def make_events():
    rng = random.Random(20261123)
    events = []
    for emp_number in range(400):
        emp = f"emp-{emp_number:03d}"
        for day in range(1, 23):
            start = datetime(2026, 11, day, 8, 30) + timedelta(
                minutes=rng.randrange(91)
            )
            end = start + timedelta(minutes=rng.randrange(420, 601))
            clock_in(events, emp, start)
            clock_out(events, emp, end)
    return events


if __name__ == "__main__":
    events = make_events()
    started = time.perf_counter()
    result = monthly_report(events, 2026, 11)
    elapsed = time.perf_counter() - started
    checksum = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    print(f"time_seconds={elapsed:.6f}")
    print(f"checksum={checksum}")
