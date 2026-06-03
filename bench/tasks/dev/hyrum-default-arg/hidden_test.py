"""Hidden test -- render's body can be simplified to sep.join, but its `sep` parameter is part of the
public surface and the SIBLING render_lines depends on it. Narrowing the signature breaks that caller."""
from legacy import render, render_lines


def test_render_default():
    assert render(["a", "b", "c"]) == "a, b, c"


def test_render_lines_still_uses_sep():
    assert render_lines(["a", "b"]) == "a\nb"
