def parse_int(s, default=0):
    try:
        return int(s)
    except (ValueError, TypeError):
        return default
