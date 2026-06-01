from legacy import clamp

def test_above():
    assert clamp(15, 0, 10) == 10

def test_below():
    assert clamp(-3, 0, 10) == 0
