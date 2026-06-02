"""Excerpt: settings.py -- parse_bool reads feature flags from environment strings."""
import os
from legacy import parse_bool


def feature_enabled(name, default="false"):
    # Operators disable a feature by setting its env var to a string. Observed behavior:
    #   parse_bool("false") -> False    parse_bool("0") -> False    parse_bool("off") -> False
    #   parse_bool("true")  -> True     parse_bool("1") -> True     parse_bool("yes") -> True
    # In production we currently ship with FAST_CHECKOUT=false, ANALYTICS=0, BETA_UI=off.
    return parse_bool(os.environ.get(name, default))
