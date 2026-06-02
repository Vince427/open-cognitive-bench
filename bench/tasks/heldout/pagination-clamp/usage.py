"""Excerpt: api.py -- page() backs the GET /orders?page=N endpoint behind an infinite-scroll UI."""
from legacy import page


def list_orders(all_orders, page_num, size=20):
    # The mobile client keeps incrementing page_num as the user scrolls and routinely overshoots the
    # end. Observed behavior the scroll UI is built on (orders 1..45, size 20):
    #   page(orders,  2, 20) -> orders 21..40   # a normal middle page
    #   page(orders, 99, 20) -> orders 41..45   # past the end: lands on the final page, not an empty list
    #   page(orders,  0, 20) -> orders  1..20   # page 0 behaves like page 1
    return page(all_orders, page_num, size)
