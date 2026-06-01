"""HIDDEN test — NOT shown to the agent. Requires sorting and even-length averaging."""
from legacy import median


def test_even_length():
    assert median([1, 2, 3, 4]) == 2.5


def test_unsorted_odd():
    assert median([3, 1, 2]) == 2


def test_unsorted_even():
    assert median([10, 2, 8, 4]) == 6
