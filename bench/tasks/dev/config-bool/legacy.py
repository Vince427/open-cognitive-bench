_FALSE = {"", "0", "false", "no", "off", "none"}


def parse_bool(s):
    # Values come from env/config as strings. "false"/"0"/"off" MUST be False.
    # Note: bool("false") is True in Python, so str truthiness cannot be used here.
    if s is None:
        return False
    return str(s).strip().lower() not in _FALSE
