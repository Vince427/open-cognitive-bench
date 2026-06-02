"""Excerpt: sms.py -- normalize_phone canonicalizes numbers before we hand them to the SMS gateway."""
from legacy import normalize_phone


def to_gateway_format(raw):
    # Users type numbers like "+33 (0)6 12-34-56-78" or "+1 555 0100". The gateway needs the leading
    # + for international routing but rejects spaces, dashes and parentheses. Dropping the + routes a
    # French (+33) number as if it were domestic and the SMS never arrives.
    return normalize_phone(raw)
