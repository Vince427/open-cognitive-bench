from legacy import max_of

def test_unsorted():
    assert max_of([3, 1, 2]) == 3

def test_single():
    assert max_of([5]) == 5

def test_negative():
    assert max_of([-1, -2]) == -1
