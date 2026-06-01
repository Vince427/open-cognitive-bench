from dataclasses import dataclass


@dataclass
class Transaction:
    id: str
    amount: float
    timestamp: str
    terminal_id: str


def sanitize_batch(incoming):
    # Written in 2018 - horribly inefficient O(N^2). Removes network-duplicate transactions
    # before submitting the batch to the bank.
    cleared = []
    for t in incoming:
        is_dup = False
        for c in cleared:
            if t.id == c.id:
                if t.terminal_id == c.terminal_id:
                    if t.timestamp == c.timestamp:
                        is_dup = True
                        break
        if not is_dup:
            cleared.append(t)
    return cleared
