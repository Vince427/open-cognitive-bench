"""Shared money helpers (excerpt of the project's `helpers` module). Read-only context: this is the
ACTUAL surface available to you -- it defines `to_cents` and nothing else."""


def to_cents(amount_str):
    """Parse a dollar string like '1.50' into integer cents (-> 150)."""
    dollars, cents = amount_str.split(".")
    return int(dollars) * 100 + int(cents)
