"""Excerpt: dashboard.py -- average() feeds a product-rating widget rendered on every product page."""
from legacy import average


def rating_widget(reviews):
    # Brand-new products have no reviews yet, but the widget is still rendered on their page.
    score = average([r.stars for r in reviews])
    return f"{score:.1f} / 5"   # must render even with an empty review list, never blow up the page
