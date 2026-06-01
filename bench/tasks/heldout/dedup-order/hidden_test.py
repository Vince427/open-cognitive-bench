from legacy import dedup

def test_removes_dupes():
    assert dedup([1, 1, 2]) == [1, 2]

def test_preserves_order():
    assert dedup([3, 1, 3, 2, 1]) == [3, 1, 2]
