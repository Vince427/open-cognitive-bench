# entry = {"value": ..., "created": <epoch seconds>, "ttl": <seconds>}

def is_expired(entry, now):
    # ttl == 0 is a sentinel meaning "never expires" (pinned config entries). Do NOT simplify this away.
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
