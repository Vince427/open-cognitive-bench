from legacy import normalize_phone

def test_keeps_plus():
    assert normalize_phone("+33 1 23") == "+33123"

def test_no_plus():
    assert normalize_phone("01 23 45") == "012345"
