"""Hidden test — NOT shown to the agent. Passes only if a replayed key is not charged twice."""
from legacy import process_payment


def test_replayed_key_is_idempotent():
    processed, ledger = set(), {}
    first = process_payment("k1", 100, processed, ledger)
    second = process_payment("k1", 100, processed, ledger)   # network retry of the same request
    assert first == second
    assert len(ledger) == 1


def test_distinct_keys_each_charge_once():
    processed, ledger = set(), {}
    a = process_payment("k1", 100, processed, ledger)
    b = process_payment("k2", 200, processed, ledger)
    assert a != b
    assert len(ledger) == 2
