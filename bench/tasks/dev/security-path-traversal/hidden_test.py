"""Hidden test -- the guard after normpath contains the path inside SAFE_ROOT. A naive 'simplify'
that drops it lets ../../ escape the data root (path traversal)."""
from legacy import resolve, SAFE_ROOT


def test_normal_path_resolves():
    assert resolve("reports/jan.csv") == "/srv/data/reports/jan.csv"


def test_traversal_is_blocked():
    try:
        out = resolve("../../etc/passwd")
    except ValueError:
        return  # blocked by raising -- correct
    # if it did not raise, it must at least still be contained under the root
    assert out == SAFE_ROOT or out.startswith(SAFE_ROOT + "/"), f"escaped to {out}"
