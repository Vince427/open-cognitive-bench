import re


def slugify(text):
    # lowercase; runs of non-alphanumerics -> single dash; trim edge dashes
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return s.strip("-")
