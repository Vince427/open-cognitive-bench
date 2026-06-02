def process_payment(key, amount, processed, ledger):
    if key in processed:
        return ledger[key]
    charge_id = "chg_%d" % (len(ledger) + 1)
    ledger[key] = charge_id
    processed.add(key)
    return charge_id
