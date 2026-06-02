"""Excerpt: payment_plan.py -- split_installments builds an installment schedule."""
from legacy import split_installments


def schedule(total_cents, n_months):
    parts = split_installments(total_cents, n_months)
    # Each `part` is charged as a separate transaction. Accounting reconciles the sum of the
    # installments against the order total down to the cent -- a one-cent drift fails the audit.
    # e.g. 1000 cents over 3 months must sum back to exactly 1000 (e.g. 334 + 333 + 333).
    assert sum(parts) == total_cents
    return parts
