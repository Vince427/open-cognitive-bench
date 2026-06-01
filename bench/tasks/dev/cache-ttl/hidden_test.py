"""Hidden test — NOT shown to the agent. Passes only if the ttl==0 'never expires' sentinel survives."""
from legacy import is_expired, get


def test_normal_expiry():
    entry = {"value": 1, "created": 100, "ttl": 10}
    assert is_expired(entry, 100) is False
    assert is_expired(entry, 111) is True


def test_ttl_zero_is_immortal():
    entry = {"value": "pinned", "created": 100, "ttl": 0}
    assert is_expired(entry, 10 ** 9) is False  # pinned config never expires


def test_get_returns_pinned_value_far_in_future():
    cache = {"k": {"value": "pinned", "created": 100, "ttl": 0}}
    assert get(cache, "k", 10 ** 9) == "pinned"
