"""Excerpt: config.py -- parse_int reads tunables from environment variables."""
import os
from legacy import parse_int


# Env vars are strings and are often unset or mistyped in deployment manifests. We want a sane
# default rather than crashing the whole service on boot because someone wrote MAX_RETRIES="" or
# TIMEOUT_S="eight".
MAX_RETRIES = parse_int(os.environ.get("MAX_RETRIES"), default=3)   # None when the var is unset
TIMEOUT_S = parse_int(os.environ.get("TIMEOUT_S", "30"))
