from legacy import count_vowels

def test_word():
    assert count_vowels("hello") == 2

def test_upper():
    assert count_vowels("AEIOU") == 5
