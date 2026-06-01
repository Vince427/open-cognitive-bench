from datetime import timedelta


def add_business_days(start, n):
    # Skip weekends (Mon=0 .. Sun=6; Sat=5, Sun=6). The day-by-day loop is intentional:
    # business days are not calendar days, so we cannot just add n.
    d = start
    added = 0
    while added < n:
        d = d + timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d
