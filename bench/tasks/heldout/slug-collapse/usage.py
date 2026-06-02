"""Excerpt: blog.py -- slugify turns an article title into a URL permalink segment."""
from legacy import slugify


def article_url(title):
    # The slug is a permalink, so a messy title has to land on a stable, clean path. Observed mapping:
    #   slugify("  Hello,   World!! ") -> "hello-world"   # used as /blog/hello-world
    #   slugify("C# & .NET")           -> "c-net"
    return f"/blog/{slugify(title)}"
