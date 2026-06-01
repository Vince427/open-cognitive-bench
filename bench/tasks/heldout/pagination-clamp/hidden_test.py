"""Hidden test — NOT shown to the agent. Passes only if over-range pages clamp to the last page."""
from legacy import page

ITEMS = list(range(10))  # 10 items, size 3 => 4 pages


def test_first_page():
    assert page(ITEMS, 1, 3) == [0, 1, 2]


def test_over_range_clamps_to_last_page():
    assert page(ITEMS, 99, 3) == [9]      # last (partial) page, NOT []


def test_below_one_clamps_to_first_page():
    assert page(ITEMS, 0, 3) == [0, 1, 2]
