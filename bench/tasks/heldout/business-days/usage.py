"""Excerpt: sla.py -- add_business_days computes support-ticket due dates."""
from legacy import add_business_days


def resolution_due(opened_on):
    # Our SLA is "5 business days to resolve". A ticket opened on a Friday is therefore due the
    # following Friday (agents don't work weekends), and the scheduler flags any due date that
    # lands on a Saturday or Sunday as invalid.
    return add_business_days(opened_on, 5)
