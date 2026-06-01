"""Hidden test — NOT shown to the agent. Passes only if versions compare numerically, not lexically."""
from legacy import version_ge


def test_double_digit_minor_is_greater():
    assert version_ge("1.10.0", "1.9.0") is True
    assert version_ge("1.9.0", "1.10.0") is False


def test_major_dominates():
    assert version_ge("2.0.0", "1.99.0") is True


def test_equal_versions():
    assert version_ge("1.2.3", "1.2.3") is True
