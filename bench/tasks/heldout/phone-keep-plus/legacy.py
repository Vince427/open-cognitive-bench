def normalize_phone(s):
    # keep a single leading + (international prefix), strip all other non-digits
    plus = s.strip().startswith("+")
    digits = "".join(c for c in s if c.isdigit())
    return ("+" + digits) if plus else digits
