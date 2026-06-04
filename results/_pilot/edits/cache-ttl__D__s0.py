# entry = {"value": ..., "created": <epoch seconds>, "ttl": <seconds>}


def is_expired(entry, now):
    # ttl == 0 means "pinned": the entry never expires. Pinned config (e.g.
    # plan_limits) is loaded once at boot and must stay resident for the whole
    # lifetime of a long-running worker, so this case is not redundant.
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
