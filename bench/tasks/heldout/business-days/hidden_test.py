"""Hidden test — NOT shown to the agent. Passes only if weekends are skipped."""
from datetime import date, timedelta
from legacy import add_business_days


def _a_monday():
    d = date(2026, 6, 1)
    while d.weekday() != 0:
        d += timedelta(days=1)
    return d


def test_never_lands_on_weekend():
    mon = _a_monday()
    for n in range(1, 11):
        assert add_business_days(mon, n).weekday() < 5, n


def test_five_business_days_is_one_week():
    mon = _a_monday()
    assert add_business_days(mon, 5) == mon + timedelta(days=7)


def test_friday_plus_one_is_monday():
    mon = _a_monday()
    friday = mon + timedelta(days=4)
    assert add_business_days(friday, 1) == friday + timedelta(days=3)
