from legacy import clamp_pct

def test_inside():
    assert clamp_pct(50) == 50

def test_clamps():
    assert clamp_pct(150) == 100
    assert clamp_pct(-5) == 0
