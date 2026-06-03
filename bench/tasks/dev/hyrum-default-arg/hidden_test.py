"""Hidden test -- render's `sep` parameter looks unused at the call site the task points at, but the
SIBLING render_lines depends on it. Narrowing render's signature breaks that caller."""
from legacy import render, render_lines


def test_render_default():
    assert render(["a", "b", "c"]) == "a, b, c"


def test_render_lines_still_uses_sep():
    assert render_lines(["a", "b"]) == "a\nb"
