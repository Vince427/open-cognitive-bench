from legacy import unique_count

def test_three():
    assert unique_count([1, 2, 3]) == 3

def test_empty():
    assert unique_count([]) == 0

def test_mixed():
    assert unique_count([5, 5, 6]) == 2
