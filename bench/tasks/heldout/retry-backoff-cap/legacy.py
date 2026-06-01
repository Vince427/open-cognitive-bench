def backoff(attempt, base=1, cap=30):
    # exponential, but capped so we never sleep absurdly long
    delay = base * (2 ** attempt)
    if delay > cap:
        return cap
    return delay
