from legacy import truncate

def test_no_truncate():
    assert truncate("abc", 5) == "abc"

def test_truncate_with_ellipsis():
    r = truncate("abcdefgh", 6)
    assert len(r) == 6 and r.endswith("...")
