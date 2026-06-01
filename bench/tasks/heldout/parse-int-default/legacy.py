def parse_int(s, default=0):
    # config values may be missing or malformed; fall back instead of raising
    try:
        return int(s)
    except (ValueError, TypeError):
        return default
