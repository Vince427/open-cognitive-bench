"""Excerpt: payment_webhook.py -- process_payment is the handler for incoming charge requests."""
from legacy import process_payment


def handle(request, processed, ledger):
    # The payment gateway re-delivers the same webhook (carrying the SAME idempotency key) whenever it
    # doesn't receive a fast 200 -- network blips make this routine, so the same key arrives several
    # times. The customer must be charged once and see one ledger entry no matter how many times the
    # gateway replays the delivery.
    return process_payment(request.idempotency_key, request.amount, processed, ledger)
