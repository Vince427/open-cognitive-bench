"""Excerpt: metrics.py -- safe_divide computes a conversion rate for the analytics table."""
from legacy import safe_divide


def conversion_rate(conversions, visits):
    # New campaigns can have zero visits in the current window; those rows show 0%. This runs over
    # every campaign when rendering the dashboard, so a single zero-visit campaign must not blow up
    # the whole report.
    return safe_divide(conversions, visits)
