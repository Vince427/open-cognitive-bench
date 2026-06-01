from legacy import slugify

def test_basic():
    assert slugify("Hello World") == "hello-world"

def test_collapses_and_trims():
    assert slugify("  A  B! ") == "a-b"
    assert slugify("x---y") == "x-y"
