from legacy import apply_discount

def test_normal():
    assert apply_discount(100, 30) == 70

def test_cap_at_zero():
    assert apply_discount(10, 15) == 0
