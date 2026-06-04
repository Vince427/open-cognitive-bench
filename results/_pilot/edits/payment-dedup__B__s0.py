from dataclasses import dataclass


@dataclass
class Transaction:
    id: str
    amount: float
    timestamp: str
    terminal_id: str


def sanitize_batch(incoming):
    # Removes network-duplicate transactions before submitting the batch to the bank.
    # A duplicate is one that matches an earlier transaction on id, terminal_id, and
    # timestamp. Uses a seen-set for O(N) deduplication while preserving input order.
    seen = set()
    cleared = []
    for t in incoming:
        key = (t.id, t.terminal_id, t.timestamp)
        if key not in seen:
            seen.add(key)
            cleared.append(t)
    return cleared
