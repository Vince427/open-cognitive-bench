from dataclasses import dataclass


@dataclass
class Transaction:
    id: str
    amount: float
    timestamp: str
    terminal_id: str


def sanitize_batch(incoming):
    # Removes network-duplicate transactions before submitting the batch to the
    # bank. A transaction is only a duplicate when its id, terminal_id, AND
    # timestamp all match a previously seen transaction; the same id from a
    # different terminal or at a different time is a distinct, legitimate
    # transaction and must be kept. Order of first appearance is preserved.
    seen = set()
    cleared = []
    for t in incoming:
        key = (t.id, t.terminal_id, t.timestamp)
        if key in seen:
            continue
        seen.add(key)
        cleared.append(t)
    return cleared
