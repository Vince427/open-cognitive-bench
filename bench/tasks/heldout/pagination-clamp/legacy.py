def page(items, page_num, size):
    # page_num is 1-based.
    if size <= 0:
        return []
    total_pages = (len(items) + size - 1) // size
    if total_pages == 0:
        return []
    p = min(page_num, total_pages)
    p = max(p, 1)
    start = (p - 1) * size
    return items[start:start + size]
