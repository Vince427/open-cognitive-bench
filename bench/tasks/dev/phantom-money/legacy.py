def total_cents(amounts):
    total = 0
    for amount_str in amounts:
        dollars, cents = amount_str.split(".")
        total += int(dollars) * 100 + int(cents)
    return total
