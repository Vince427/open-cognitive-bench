def split_installments(total_cents, n):
    # Split an integer amount of cents into n installments.
    base = total_cents // n
    installments = [base] * n
    remainder = total_cents - base * n
    i = 0
    while remainder > 0:
        installments[i] += 1
        remainder -= 1
        i += 1
    return installments
