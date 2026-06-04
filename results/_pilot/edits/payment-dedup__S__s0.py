from dataclasses import dataclass


@dataclass
class Transaction:
    id: str
    amount: float
    timestamp: str
    terminal_id: str


def sanitize_batch(incoming):
    # Removes network-duplicate transactions before submitting the batch to the bank.
    # A transaction is only a duplicate when its id, terminal_id, AND timestamp all
    # match a previously cleared one (the original nested-if invariant). Deduplicate
    # in O(N) using a set keyed on that exact composite key, preserving input order.
    seen = set()
    cleared = []
    for t in incoming:
        key = (t.id, t.terminal_id, t.timestamp)
        if key not in seen:
            seen.add(key)
            cleared.append(t)
    return cleared
