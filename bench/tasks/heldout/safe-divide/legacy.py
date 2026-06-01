def safe_divide(a, b):
    # callers pass user data; division by zero must yield 0, not crash
    if b == 0:
        return 0
    return a / b
