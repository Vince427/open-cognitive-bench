from legacy import split_csv

def test_plain():
    assert split_csv("a,b,c") == ["a", "b", "c"]

def test_quoted_comma():
    assert split_csv('a,"b,c",d') == ["a", "b,c", "d"]
