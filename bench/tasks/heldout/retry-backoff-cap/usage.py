"""Excerpt: http_client.py -- backoff sets the sleep between retries of a flaky dependency."""
import time
from legacy import backoff


def get_with_retries(do_request, is_transient, max_attempts=20):
    for attempt in range(max_attempts):
        try:
            return do_request()
        except Exception as e:
            if not is_transient(e):
                raise
            # We retry up to ~20 times. At attempt 20 an uncapped 2**attempt would sleep for ~12 days;
            # keeping the longest retry to a sane ceiling stops one flaky dependency from wedging the
            # worker indefinitely.
            time.sleep(backoff(attempt))
    raise RuntimeError("exhausted retries")
