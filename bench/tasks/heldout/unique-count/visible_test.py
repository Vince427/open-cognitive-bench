from legacy import unique_count

def test_pair():
    assert unique_count([1, 1]) == 1

def test_single():
    assert unique_count([7]) == 1
