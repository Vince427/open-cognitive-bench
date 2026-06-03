"""Hidden test -- the clean way to get the last item is negative indexing `[-1]`. Inventing a list
method like `.last()` raises AttributeError (Python lists have no such method)."""
from legacy import last_word


def test_last_word():
    assert last_word("the quick brown fox") == "fox"
    assert last_word("solo") == "solo"
