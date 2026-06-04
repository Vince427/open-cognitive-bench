from helpers import to_cents


def total_cents(amounts):
    total = 0
    for amount_str in amounts:
        total += to_cents(amount_str)
    return total
