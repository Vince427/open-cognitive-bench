from legacy import gcd

def test_common():
    assert gcd(12, 18) == 6

def test_coprime():
    assert gcd(17, 5) == 1
