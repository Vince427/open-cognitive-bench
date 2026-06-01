from legacy import flatten

def test_ragged():
    assert flatten([[1, 2], [], [3]]) == [1, 2, 3]

def test_empty():
    assert flatten([]) == []
