def truncate(text, limit):
    # only add an ellipsis if we actually cut; the ellipsis counts toward the limit
    if len(text) <= limit:
        return text
    return text[:limit - 3] + "..."
