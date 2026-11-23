"""Simple, in-memory attendance tracking.

Events are dictionaries with emp, ts (a datetime), and type keys.
A shift belongs to the calendar day and month of its clock-in.
"""
from datetime import time


def clock_in(events, emp, ts):
    """Append a clock-in, rejecting a second one for an open shift."""
    for event in reversed(events):
        if event["emp"] == emp:
            if event["type"] == "in":
                raise ValueError(f"{emp} is already clocked in")
            break
    events.append({"type": "in", "emp": emp, "ts": ts})
    return events


def clock_out(events, emp, ts):
    """Append a clock-out only when the employee has an open shift."""
    for event in reversed(events):
        if event["emp"] == emp:
            if event["type"] != "in":
                break
            if ts <= event["ts"]:
                raise ValueError("clock-out must follow clock-in")
            events.append({"type": "out", "emp": emp, "ts": ts})
            return events
    raise ValueError(f"{emp} is not clocked in")


def monthly_report(events, year, month):
    """Summarize completed shifts by employee and clock-in date.

    Unfinished shifts contribute no hours or days. A day is late if its first
    clock-in is after 09:00. Overtime is time beyond eight hours that day.
    """
    report = {}
    employees = sorted({event["emp"] for event in events})
    for emp in employees:
        employee_events = [event for event in events if event["emp"] == emp]
        opened = None
        daily = {}
        for event in employee_events:
            if event["type"] == "in":
                opened = event["ts"]
            elif opened is not None:
                day = opened.date()
                if day.year == year and day.month == month:
                    record = daily.setdefault(
                        day, {"hours": 0.0, "first_in": opened.time()}
                    )
                    record["hours"] += (
                        event["ts"] - opened
                    ).total_seconds() / 3600
                    if opened.time() < record["first_in"]:
                        record["first_in"] = opened.time()
                opened = None
        if daily:
            report[emp] = {
                "days": len(daily),
                "total_hours": round(
                    sum(item["hours"] for item in daily.values()), 2
                ),
                "late_days": sum(
                    item["first_in"] > time(9, 0) for item in daily.values()
                ),
                "overtime_hours": round(
                    sum(
                        max(0.0, item["hours"] - 8)
                        for item in daily.values()
                    ),
                    2,
                ),
            }
    return report
