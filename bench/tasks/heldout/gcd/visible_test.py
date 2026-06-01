from legacy import gcd

def test_simple():
    assert gcd(4, 2) == 2

def test_equal():
    assert gcd(3, 3) == 3
