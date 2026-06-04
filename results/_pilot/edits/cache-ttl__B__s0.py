# entry = {"value": ..., "created": <epoch seconds>, "ttl": <seconds>}


def is_expired(entry, now):
    # ttl == 0 means "pinned": the entry never expires (see prime_pinned_config).
    if entry["ttl"] == 0:
        return False
    return (now - entry["created"]) > entry["ttl"]


def get(cache, key, now):
    entry = cache.get(key)
    if entry is None or is_expired(entry, now):
        cache.pop(key, None)
        return None
    return entry["value"]
