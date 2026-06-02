"""Excerpt: api.py -- page() backs the GET /orders?page=N endpoint."""
from legacy import page


def list_orders(all_orders, page_num, size=20):
    # The mobile client keeps incrementing page_num as the user scrolls and routinely requests a page
    # past the end. Product decided that should return the last page of results (so the list never
    # goes blank at the bottom), and that page_num of 0 or negative should return the first page.
    return page(all_orders, page_num, size)
