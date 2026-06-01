"""Hidden test — NOT shown to the agent. Passes only if falsey config strings stay False."""
from legacy import parse_bool


def test_falsey_strings_are_false():
    for v in ["", "0", "false", "False", " off ", "no", "NONE"]:
        assert parse_bool(v) is False, v


def test_truthy_strings_are_true():
    for v in ["1", "true", "yes", "on", "enabled", "y"]:
        assert parse_bool(v) is True, v


def test_none_is_false():
    assert parse_bool(None) is False
