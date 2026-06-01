from legacy import merge

def test_override_wins():
    assert merge({"a": 1}, {"a": 2}) == {"a": 2}

def test_none_does_not_clobber():
    assert merge({"a": 1}, {"a": None}) == {"a": 1}
