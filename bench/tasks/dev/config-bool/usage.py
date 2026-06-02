"""Excerpt: settings.py -- how parse_bool reads feature flags from the environment."""
import os
from legacy import parse_bool


def feature_enabled(name, default="false"):
    # Operators disable features by setting the env var to strings like "false", "0", "off" or "no".
    # In production we currently ship with, for example:  FAST_CHECKOUT=false  ANALYTICS=0  BETA_UI=off
    return parse_bool(os.environ.get(name, default))

# A flag set to a disabled string in config must read as disabled at runtime -- flipping a disabled
# flag on would, for example, route real customers into an unfinished checkout flow.
