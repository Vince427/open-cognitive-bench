import posixpath

SAFE_ROOT = "/srv/data"


def resolve(user_path):
    full = posixpath.normpath(posixpath.join(SAFE_ROOT, user_path))
    if full == SAFE_ROOT or full.startswith(SAFE_ROOT + "/"):
        return full
    raise ValueError("path escapes data root")
