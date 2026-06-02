def normalize_phone(s):
    plus = s.strip().startswith("+")
    digits = "".join(c for c in s if c.isdigit())
    return ("+" + digits) if plus else digits
