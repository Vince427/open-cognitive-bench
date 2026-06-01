def process_payment(key, amount, processed, ledger):
    # Idempotency: network retries replay the same request. Never charge the same key twice —
    # return the existing charge id instead. (The early return is the invariant, not redundancy.)
    if key in processed:
        return ledger[key]
    charge_id = "chg_%d" % (len(ledger) + 1)
    ledger[key] = charge_id
    processed.add(key)
    return charge_id
