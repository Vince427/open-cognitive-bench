def clamp_pct(v):
    # progress percentage must stay within [0, 100] even if the raw value overshoots
    if v < 0:
        return 0
    if v > 100:
        return 100
    return v
