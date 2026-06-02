"""Excerpt: blog.py -- slugify turns an article title into a URL path segment."""
from legacy import slugify


def article_url(title):
    # A title like "  Hello,   World!! " must become the clean slug "hello-world": no leading or
    # trailing dashes and no doubled dashes, because the slug is a permalink and a URL such as
    # "/blog/hello--world-" would 404.
    return f"/blog/{slugify(title)}"
