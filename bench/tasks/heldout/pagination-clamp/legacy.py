def page(items, page_num, size):
    # page_num is 1-based. Over-range pages clamp to the LAST page (UI contract: never show a blank
    # page when the user pages past the end); page_num < 1 clamps to the first page.
    if size <= 0:
        return []
    total_pages = (len(items) + size - 1) // size
    if total_pages == 0:
        return []
    p = min(page_num, total_pages)
    p = max(p, 1)
    start = (p - 1) * size
    return items[start:start + size]
