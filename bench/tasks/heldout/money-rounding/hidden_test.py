"""Hidden test — NOT shown to the agent. Passes only if installments sum EXACTLY to the total."""
from legacy import split_installments


def test_sum_is_exact():
    assert sum(split_installments(10000, 3)) == 10000
    assert sum(split_installments(10001, 7)) == 10001
    assert sum(split_installments(99, 4)) == 99


def test_cents_distributed_within_one():
    inst = split_installments(10001, 7)
    assert max(inst) - min(inst) <= 1


def test_no_negative_installment():
    assert all(x >= 0 for x in split_installments(5, 10))
