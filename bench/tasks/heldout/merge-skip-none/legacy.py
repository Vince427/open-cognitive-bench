def merge(base, override):
    out = dict(base)
    for k, v in override.items():
        if v is not None:
            out[k] = v
    return out
