def dedup(items):
    # preserve first-seen order (set() would lose it)
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
