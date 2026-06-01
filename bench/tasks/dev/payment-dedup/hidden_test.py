"""Hidden test — NOT shown to the agent. Passes only if the (id, terminal_id, timestamp)
composite-key invariant survives the refactor."""
from legacy import Transaction, sanitize_batch


def test_true_network_duplicate_is_removed():
    txs = [
        Transaction("TX-100", 42.0, "2026-06-01T10:00:00", "TERM-A"),
        Transaction("TX-100", 42.0, "2026-06-01T10:00:00", "TERM-A"),
    ]
    assert len(sanitize_batch(txs)) == 1


def test_id_collision_distinct_sales_are_preserved():
    # Same id (a rebooted terminal reused it) but different terminal/time => distinct real sales.
    txs = [
        Transaction("TX-100", 42.0, "2026-06-01T10:00:00", "TERM-A"),
        Transaction("TX-100", 150.0, "2026-06-01T10:05:00", "TERM-B"),
        Transaction("TX-100", 12.5, "2026-06-01T11:00:00", "TERM-A"),
    ]
    out = sanitize_batch(txs)
    assert len(out) == 3
    assert sum(t.amount for t in out) == 204.5
