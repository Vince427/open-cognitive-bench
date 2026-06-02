"""Excerpt: table.py -- truncate fits a title into a fixed-width column."""
from legacy import truncate


def cell(title, width=20):
    # The column is exactly `width` characters wide in the terminal UI. The returned string must never
    # exceed `width` (the "..." counts toward it), or the whole table layout shifts. Titles that
    # already fit are shown in full, with no ellipsis.
    s = truncate(title, width)
    assert len(s) <= width
    return s
