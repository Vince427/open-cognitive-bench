from dataclasses import dataclass


@dataclass
class Transaction:
    id: str
    amount: float
    timestamp: str
    terminal_id: str


def sanitize_batch(incoming):
    # Removes network-duplicate transactions before submitting the batch to the bank.
    # A transaction is a duplicate only when its id, terminal_id, and timestamp all
    # match a transaction already cleared. Two transactions sharing an id but differing
    # in terminal_id or timestamp are distinct and must both be kept.
    cleared = []
    seen = set()
    for t in incoming:
        key = (t.id, t.terminal_id, t.timestamp)
        if key not in seen:
            seen.add(key)
            cleared.append(t)
    return cleared
