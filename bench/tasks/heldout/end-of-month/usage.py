"""Excerpt: billing.py -- last_day computes the final day of a billing month."""
from datetime import date
from legacy import last_day


def billing_period_end(year, month):
    # Subscriptions bill on the last day of the month. February is the awkward one: in 2024 (a leap
    # year) the February cycle must end on the 29th, in 2023 on the 28th. Getting that one day wrong
    # double-bills or skips a day for every February subscriber.
    return date(year, month, last_day(year, month))
