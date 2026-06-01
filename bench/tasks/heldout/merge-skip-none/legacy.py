def merge(base, override):
    # override wins, but a None value must NOT clobber an existing real value
    out = dict(base)
    for k, v in override.items():
        if v is not None:
            out[k] = v
    return out
