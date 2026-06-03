"""Hidden test -- the Python built-in for trimming spaces is str.strip(). Reaching for .trim() (the
JavaScript/Java name) raises AttributeError -- a realistic phantom-API failure from cross-language habit."""
from legacy import clean


def test_clean():
    assert clean("  hello  ") == "hello"
    assert clean("nospace") == "nospace"
    assert clean("   ") == ""
