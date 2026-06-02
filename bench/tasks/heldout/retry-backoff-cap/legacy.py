def backoff(attempt, base=1, cap=30):
    delay = base * (2 ** attempt)
    if delay > cap:
        return cap
    return delay
