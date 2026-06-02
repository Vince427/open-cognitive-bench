"""Excerpt: table.py -- truncate fits a title into a fixed-width column."""
from legacy import truncate


def cell(title, width=20):
    # The column is exactly `width` chars wide; a wider string shifts the whole table layout. Observed:
    #   truncate("short title", 20)         -> "short title"   # fits: returned unchanged
    #   truncate("a very long heading", 10) -> "a very ..."    # 10 chars total, including the "..."
    s = truncate(title, width)
    assert len(s) <= width
    return s
