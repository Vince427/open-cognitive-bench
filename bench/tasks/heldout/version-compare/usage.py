"""Excerpt: feature_gate.py -- version_ge decides whether a client is new enough for a feature."""
from legacy import version_ge

MIN_SUPPORTED = "1.9.0"


def supports_new_sync(client_version):
    # client_version comes from the app's User-Agent, e.g. "1.10.0" -- the tenth minor release, which
    # is newer than 1.9.0. Clients at or above MIN_SUPPORTED get the new sync protocol. Rolling out
    # 1.10.x must NOT be treated as older than 1.9.0, or we'd disable sync for the newest apps.
    return version_ge(client_version, MIN_SUPPORTED)
