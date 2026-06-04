# entry = {"value": ..., "created": <epoch seconds>, "ttl": <seconds>}


def is_expired(entry, now):
    # ttl == 0 means the entry is pinned and never expires. usage.py
    # (prime_pinned_config / read_plan_limits) relies on this: plan_limits is
    # loaded once at boot with ttl=0 and must stay resident for the whole
    # process lifetime, so this is NOT a redundant case -- it is the invariant.
    ttl = entry["ttl"]
    if ttl == 0:
        return False
    return now - entry["created"] > ttl


def get(cache, key, now):
    entry = cache.get(key)
    if entry is None:
        return None
    if is_expired(entry, now):
        del cache[key]
        return None
    return entry["value"]
