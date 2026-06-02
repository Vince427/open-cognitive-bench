import re


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return s.strip("-")
