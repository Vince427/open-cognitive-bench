"""Excerpt: feature_gate.py -- version_ge gates a feature on the client's app version."""
from legacy import version_ge

MIN_SUPPORTED = "1.9.0"


def supports_new_sync(client_version):
    # client_version comes from the app's User-Agent. Observed behavior the gate relies on:
    #   version_ge("1.10.0", "1.9.0")  -> True     # 1.10 is the tenth minor, newer than 1.9
    #   version_ge("1.2.0",  "1.10.0") -> False
    return version_ge(client_version, MIN_SUPPORTED)
