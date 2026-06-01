from legacy import flatten

def test_two_singletons():
    assert flatten([[1], [2]]) == [1, 2]
