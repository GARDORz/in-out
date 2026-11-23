from datetime import datetime

import pytest

from src.attendance import clock_in, clock_out, monthly_report


def dt(day, hour, minute=0, month=11):
    return datetime(2026, month, day, hour, minute)


def test_normal_clock_in_and_out():
    events = []
    assert clock_in(events, "e1", dt(1, 9)) is events
    assert clock_out(events, "e1", dt(1, 17)) is events
    assert monthly_report(events, 2026, 11) == {
        "e1": {
            "days": 1,
            "total_hours": 8.0,
            "late_days": 0,
            "overtime_hours": 0.0,
        }
    }


def test_duplicate_clock_in():
    events = []
    clock_in(events, "e1", dt(1, 9))
    with pytest.raises(ValueError):
        clock_in(events, "e1", dt(1, 10))
    assert len(events) == 1


def test_clock_out_before_clock_in():
    with pytest.raises(ValueError):
        clock_out([], "e1", dt(1, 17))


def test_late_and_overtime():
    events = []
    clock_in(events, "e1", dt(1, 9, 1))
    clock_out(events, "e1", dt(1, 19, 1))
    assert monthly_report(events, 2026, 11)["e1"] == {
        "days": 1,
        "total_hours": 10.0,
        "late_days": 1,
        "overtime_hours": 2.0,
    }


def test_multiple_shifts_on_one_day():
    events = []
    clock_in(events, "e1", dt(1, 8))
    clock_out(events, "e1", dt(1, 12))
    clock_in(events, "e1", dt(1, 13))
    clock_out(events, "e1", dt(1, 18))
    assert monthly_report(events, 2026, 11)["e1"] == {
        "days": 1,
        "total_hours": 9.0,
        "late_days": 0,
        "overtime_hours": 1.0,
    }


def test_filter_by_month():
    events = []
    clock_in(events, "e1", dt(1, 9, month=10))
    clock_out(events, "e1", dt(1, 17, month=10))
    clock_in(events, "e1", dt(1, 9))
    clock_out(events, "e1", dt(1, 18))
    assert monthly_report(events, 2026, 11)["e1"]["total_hours"] == 9.0
    assert monthly_report(events, 2026, 10)["e1"]["total_hours"] == 8.0


def test_no_data():
    assert monthly_report([], 2026, 11) == {}


def test_open_shift_is_not_counted():
    events = []
    clock_in(events, "e1", dt(1, 9))
    assert monthly_report(events, 2026, 11) == {}


def test_employees_are_independent():
    events = []
    clock_in(events, "e1", dt(1, 9))
    clock_in(events, "e2", dt(1, 10))
    clock_out(events, "e1", dt(1, 17))
    clock_out(events, "e2", dt(1, 18))
    report = monthly_report(events, 2026, 11)
    assert report["e1"]["late_days"] == 0
    assert report["e2"]["late_days"] == 1


def test_second_clock_out_is_rejected():
    events = []
    clock_in(events, "e1", dt(1, 9))
    clock_out(events, "e1", dt(1, 17))
    with pytest.raises(ValueError):
        clock_out(events, "e1", dt(1, 18))
