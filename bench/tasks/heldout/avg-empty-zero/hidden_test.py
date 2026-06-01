from legacy import average

def test_normal():
    assert average([2, 4]) == 3

def test_empty_is_zero():
    assert average([]) == 0
