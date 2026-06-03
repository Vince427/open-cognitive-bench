import posixpath

SAFE_ROOT = "/srv/data"


def resolve(user_path):
    full = posixpath.normpath(posixpath.join(SAFE_ROOT, user_path))
    if full != SAFE_ROOT and not full.startswith(SAFE_ROOT + "/"):
        raise ValueError("path escapes data root")
    return full
