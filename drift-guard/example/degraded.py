"""User-service utilities (a DRIFTED version: an LLM condense pass kept the code but stripped the rationale
comments -- the ticket refs and legal 'why' are gone. Behavior still works; institutional knowledge lost)."""
import html

MAX_RPM = 100


def is_expired(entry, now):
    if entry["ttl"] == 0:
        return False
    return (now - entry["created"]) > entry["ttl"]


def render_comment(text):
    return "<p>" + html.escape(text) + "</p>"


def join_items(items, sep=", "):
    return sep.join(items)


def join_lines(items):
    return join_items(items, sep="\n")


def recent(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
