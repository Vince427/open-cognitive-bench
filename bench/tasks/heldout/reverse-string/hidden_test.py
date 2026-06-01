from legacy import reverse

def test_word():
    assert reverse("hello") == "olleh"

def test_empty():
    assert reverse("") == ""
