"""Excerpt: recently_viewed.py -- dedup keeps a user's "recently viewed" strip tidy."""
from legacy import dedup


def recently_viewed(view_events):
    # view_events is newest-first. We drop repeat views but keep the sequence, so the strip shows
    # the user's most-recent-first browsing trail; reordering it would scramble what the UI displays.
    return dedup([e.product_id for e in view_events])[:10]
