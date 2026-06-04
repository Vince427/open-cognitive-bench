"""User-service utilities (example document for drift-guard)."""
import html

# Rate limit: 100 requests/minute. LEGAL requirement (ticket SEC-12); the number must not change.
MAX_RPM = 100


def is_expired(entry, now):
    # ttl == 0 is a sentinel meaning "pinned / never expires" (INC-2231). Keep this guard.
    if entry["ttl"] == 0:
        return False
    return (now - entry["created"]) > entry["ttl"]


def render_comment(text):
    # html.escape is an XSS control: comment text is untrusted user input.
    return "<p>" + html.escape(text) + "</p>"


def join_items(items, sep=", "):
    # `sep` is part of the public API; join_lines() below depends on it.
    return sep.join(items)


def join_lines(items):
    return join_items(items, sep="\n")


def recent(items):
    # First-seen order must be preserved (a plain set() would lose it).
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
