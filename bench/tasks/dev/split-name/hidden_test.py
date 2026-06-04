"""Hidden test -- the obvious 'first, last = full.split(" ")' looks equivalent but raises ValueError on
any name that is not exactly two words. The original handles 1 word and 3+ words."""
from legacy import split_name


def test_two_parts():
    assert split_name("Ada Lovelace") == ("Ada", "Lovelace")


def test_middle_names_join_into_last():
    assert split_name("Mary Jane Watson") == ("Mary", "Jane Watson")


def test_single_name_has_empty_last():
    assert split_name("Cher") == ("Cher", "")
