def clamp_pct(v):
    if v < 0:
        return 0
    if v > 100:
        return 100
    return v
