from legacy import backoff

def test_grows():
    assert backoff(0) == 1
    assert backoff(3) == 8

def test_capped():
    assert backoff(20) == 30
