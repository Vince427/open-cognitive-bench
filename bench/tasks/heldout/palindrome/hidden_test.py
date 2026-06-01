from legacy import is_palindrome

def test_odd():
    assert is_palindrome("aba")

def test_not_palindrome():
    assert not is_palindrome("abca")

def test_even():
    assert is_palindrome("abba")
