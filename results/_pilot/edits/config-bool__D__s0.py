_FALSE = frozenset({"", "0", "false", "no", "off", "none"})


def parse_bool(s):
    if s is None:
        return False
    return str(s).strip().lower() not in _FALSE
