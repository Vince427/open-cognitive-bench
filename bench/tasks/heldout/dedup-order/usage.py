"""Excerpt: recently_viewed.py -- dedup tidies a user's "recently viewed" strip."""
from legacy import dedup


def recently_viewed(view_events):
    # view_events is newest-first and full of repeats. Observed behavior:
    #   dedup([3, 1, 2, 1, 3]) -> [3, 1, 2]   # what the strip shows: each product once, newest first
    return dedup([e.product_id for e in view_events])[:10]
