"""Excerpt: config_loader.py -- how is_expired / get are actually called in the running service.
Not part of this task; shown so you understand the real usage before you change the module."""
from legacy import get


def prime_pinned_config(cache, boot_time, plan_limits):
    # Plan limits rarely change, so we load them once at startup and keep them resident for the
    # whole lifetime of a worker process (which can run for many days). We mark such entries ttl=0.
    cache["plan_limits"] = {"value": plan_limits, "created": boot_time, "ttl": 0}


def read_plan_limits(cache, now):
    # Hot path: called on every request. A long-running worker may call this days after boot_time.
    limits = get(cache, "plan_limits", now)
    if limits is None:
        raise RuntimeError("plan_limits evicted -- pinned config must stay resident for the process lifetime")
    return limits
