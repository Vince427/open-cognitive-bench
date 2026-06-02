"""Excerpt: payment_webhook.py -- process_payment handles incoming charge webhooks."""
from legacy import process_payment


def replay_demo():
    # The gateway re-delivers the same webhook (same idempotency key) on any network blip, so the
    # handler runs more than once for a single payment. What a replay looks like in practice:
    ledger, processed = {}, set()
    first = process_payment("idem-7", 5000, processed, ledger)
    again = process_payment("idem-7", 5000, processed, ledger)   # redelivery of the same webhook
    assert first == again and len(ledger) == 1   # the customer saw one charge across both deliveries
    return first
