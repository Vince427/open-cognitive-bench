import posixpath

SAFE_ROOT = "/srv/data"


def resolve(user_path):
    joined = SAFE_ROOT + "/" + user_path
    full = posixpath.normpath(joined)
    inside = False
    if full == SAFE_ROOT:
        inside = True
    if full.startswith(SAFE_ROOT + "/"):
        inside = True
    if inside:
        return full
    raise ValueError("path escapes data root")
