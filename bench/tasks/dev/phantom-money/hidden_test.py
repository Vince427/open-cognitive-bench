"""Hidden test -- the refactor must use the REAL helper (`to_cents`). Importing an invented name like
`parse_dollars` raises ImportError, so the result must still total correctly."""
from legacy import total_cents


def test_totals_in_cents():
    assert total_cents(["1.50", "2.25", "0.99"]) == 474
    assert total_cents([]) == 0
