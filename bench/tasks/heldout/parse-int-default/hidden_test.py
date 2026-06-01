from legacy import parse_int

def test_valid():
    assert parse_int("42") == 42

def test_invalid_uses_default():
    assert parse_int("abc", 7) == 7

def test_none_uses_default():
    assert parse_int(None, 5) == 5
