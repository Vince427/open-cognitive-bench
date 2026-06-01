from legacy import last_day

def test_april():
    assert last_day(2026, 4) == 30

def test_feb_common():
    assert last_day(2023, 2) == 28

def test_feb_leap():
    assert last_day(2024, 2) == 29
