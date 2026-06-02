"""Excerpt: progress.py -- clamp_pct sets the CSS width of an upload progress bar."""
from legacy import clamp_pct


def bar_width_style(done, total):
    # `total` is an estimate sent by the client; uploads sometimes report more bytes than estimated,
    # so done/total can briefly exceed 1.0 (and a stalled/negative delta can dip below 0).
    raw = 100 * done / total if total else 0
    return f"width: {clamp_pct(raw)}%;"   # a width above 100% or below 0% breaks the page layout
