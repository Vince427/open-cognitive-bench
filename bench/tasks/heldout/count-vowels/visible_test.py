from legacy import count_vowels

def test_one():
    assert count_vowels("a") == 1

def test_none():
    assert count_vowels("b") == 0
