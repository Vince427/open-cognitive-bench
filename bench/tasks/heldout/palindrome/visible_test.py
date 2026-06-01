from legacy import is_palindrome

def test_yes():
    assert is_palindrome("aa")

def test_no():
    assert not is_palindrome("ab")
