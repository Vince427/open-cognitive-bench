# entry = {"value": ..., "created": <epoch seconds>, "ttl": <seconds>}


def is_expired(entry, now):
    # ttl == 0 means "pinned" -- the entry never expires (see usage.py: prime_pinned_config
    # marks plan_limits with ttl=0 so they stay resident for the whole worker lifetime).
    if entry["ttl"] == 0:
        return False
    return (now - entry["created"]) > entry["ttl"]


def get(cache, key, now):
    entry = cache.get(key)
    if entry is None:
        return None
    if is_expired(entry, now):
        del cache[key]
        return None
    return entry["value"]
