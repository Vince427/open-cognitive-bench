"""Unit tests for the harness logic itself (stats math, code extraction, judge execution).

`selfcheck.py` validates the *tasks*; this validates the *harness*. Pure stdlib — runs either under pytest
or directly:  python tests/test_harness.py  (exits non-zero on any failure).
"""
from __future__ import annotations
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bench"))

import run_bench  # noqa: E402
import stats       # noqa: E402
import judge       # noqa: E402
import power       # noqa: E402


# ---- extract_code (incl. the M2 fix: language tag must not leak) -------------------------------------
def test_extract_python_fence():
    assert run_bench.extract_code("```python\nx = 1\n```", "FB").strip() == "x = 1"


def test_extract_py_fence_no_leak():
    assert run_bench.extract_code("```py\nx = 1\n```", "FB").strip() == "x = 1"


def test_extract_python3_fence_no_leak():
    assert run_bench.extract_code("```python3\nx = 1\n```", "FB").strip() == "x = 1"


def test_extract_bare_fence():
    assert run_bench.extract_code("```\nx = 1\n```", "FB").strip() == "x = 1"


def test_extract_other_lang_fence():
    assert run_bench.extract_code("```ts\nx = 1\n```", "FB").strip() == "x = 1"


def test_extract_prose_then_code():
    assert run_bench.extract_code("Fence Report: blah\n```python\ncode = 2\n```", "FB").strip() == "code = 2"


def test_extract_last_block_wins():
    t = "```python\na = 1\n```\nmid\n```python\nb = 2\n```"
    assert run_bench.extract_code(t, "FB").strip() == "b = 2"


def test_extract_no_fence_returns_raw():
    assert run_bench.extract_code("sorry, I cannot", "FB") == "sorry, I cannot"


# ---- stats: McNemar exact, mean, percentile, bootstrap -----------------------------------------------
def test_mcnemar_one_sided_discordant():
    x = {i: 1 for i in range(5)}
    y = {i: 0 for i in range(5)}
    n10, n01, p = stats.mcnemar_exact(x, y, list(range(5)))
    assert (n10, n01) == (5, 0)
    assert abs(p - 2 * (0.5 ** 5)) < 1e-9  # 0.0625


def test_mcnemar_balanced_is_one():
    keys = list(range(10))
    x = {k: (1 if k < 5 else 0) for k in keys}
    y = {k: (0 if k < 5 else 1) for k in keys}
    n10, n01, p = stats.mcnemar_exact(x, y, keys)
    assert (n10, n01, p) == (5, 5, 1.0)


def test_mcnemar_no_discordant_is_one():
    keys = [0, 1, 2]
    x = {0: 1, 1: 0, 2: 1}
    assert stats.mcnemar_exact(x, dict(x), keys) == (0, 0, 1.0)


def test_mean_and_percentile():
    assert stats.mean([2, 4]) == 3
    vals = sorted([0.1, 0.2, 0.3, 0.4])
    assert stats.percentile(vals, 2.5) == 0.1
    assert stats.percentile(vals, 97.5) == 0.4


def test_bootstrap_extremes_pin_to_minus_one():
    keys = [("t%d" % i, 0) for i in range(10)]
    x = {k: 0 for k in keys}
    y = {k: 1 for k in keys}
    lo, hi = stats.bootstrap_diff_ci(x, y, keys, random.Random(0))
    assert lo == -1.0 and hi == -1.0  # X always 0, Y always 1 -> diff is always -1


def test_system_for_maps_kind_to_skill():
    assert "Chesterton's Shield" in run_bench.system_for("S", "chesterton")
    assert "Goodhart" in run_bench.system_for("S", "goodhart")
    assert "Hyrum's Shield" in run_bench.system_for("S", "hyrum")
    assert "Fail-Safe" in run_bench.system_for("S", "security")
    assert "Phantom Check" in run_bench.system_for("S", "phantom")
    assert run_bench.system_for("C", "security") != run_bench.system_for("C", "phantom")  # kind-specific caution
    assert run_bench.system_for("B", "hyrum") == ""                                       # bare arm is empty


def test_forest_row_places_markers():
    line = stats.forest_row("W vs S", -0.10, -0.20, -0.05, True, width=41, label_w=12)
    assert line.startswith("W vs S")
    bar = line.split(None, 2)[2].split(" -0.100")[0]  # the ASCII bar between label and value
    assert "[" in bar and "]" in bar and "o" in bar and "|" in bar
    assert line.endswith("-0.100 *")                  # significance marker present
    assert stats.forest_row("D vs B", 0.0, -0.1, 0.1, False).endswith("+0.000")  # no marker when n.s.


def test_bootstrap_identical_contains_zero():
    keys = [("t%d" % i, 0) for i in range(10)]
    x = {k: (i % 2) for i, k in enumerate(keys)}
    lo, hi = stats.bootstrap_diff_ci(x, dict(x), keys, random.Random(0))
    assert lo <= 0 <= hi


# ---- judge: execution runner classifies pass/fail correctly -----------------------------------------
def test_judge_runner_pass_then_fail():
    # Use two separate dirs (fresh __pycache__) — mirrors judge's per-run workdir; avoids stale-bytecode reuse.
    ht = "from legacy import f\n\ndef test_f():\n    assert f() == 1\n"
    with tempfile.TemporaryDirectory() as d1:
        d1 = Path(d1)
        (d1 / "hidden_test.py").write_text(ht, encoding="utf-8")
        (d1 / "legacy.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        assert judge.test_passes(d1, "hidden_test.py") is True
    with tempfile.TemporaryDirectory() as d2:
        d2 = Path(d2)
        (d2 / "hidden_test.py").write_text(ht, encoding="utf-8")
        (d2 / "legacy.py").write_text("def f():\n    return 2\n", encoding="utf-8")
        assert judge.test_passes(d2, "hidden_test.py") is False


def test_judge_runner_syntax_error_is_fail():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "hidden_test.py").write_text("from legacy import f\n\ndef test_f():\n    assert f() == 1\n", encoding="utf-8")
        (d / "legacy.py").write_text("def f(:\n  return 1\n", encoding="utf-8")  # malformed
        assert judge.test_passes(d, "hidden_test.py") is False


# ---- power: the Monte-Carlo power calc reuses the real stats functions & decision rule ----------------
def test_power_monotonic_in_effect_size():
    # A large true gap must yield more power than no gap (a sanity check on the simulator + decision rule).
    stats.N_BOOT = 120
    rng = random.Random(0)
    big, _, _ = power.power_for(0.10, 0.80, n_tasks=30, n_seeds=5, sigma=0.0, sims=60, rng=rng)
    none, _, _ = power.power_for(0.50, 0.50, n_tasks=30, n_seeds=5, sigma=0.0, sims=60, rng=rng)
    assert big > 0.8          # a 0.70 gap on 30x5 is trivially detectable
    assert none < 0.2         # no real effect -> rejections only at ~the (Bonferroni) false-positive rate


def test_power_realized_rates_track_inputs():
    stats.N_BOOT = 60
    _, rmX, rmY = power.power_for(0.20, 0.60, n_tasks=30, n_seeds=5, sigma=0.0, sims=40, rng=random.Random(1))
    assert abs(rmX - 0.20) < 0.06 and abs(rmY - 0.60) < 0.06   # i.i.d. case recovers the input rates


def test_power_null_controls_type_one_error():
    # Under no true effect the exact decision rule must rarely fire, even with task heterogeneity.
    stats.N_BOOT = 120
    fpr0 = power.false_positive_rate(0.40, n_tasks=30, n_seeds=5, sigma=0.0, sims=120, rng=random.Random(2))
    fpr1 = power.false_positive_rate(0.40, n_tasks=30, n_seeds=5, sigma=1.0, sims=120, rng=random.Random(3))
    assert fpr0 <= 0.05 and fpr1 <= 0.05   # generous bound for small-sims MC; target is ~0.01


if __name__ == "__main__":
    g = dict(globals())
    tests = sorted((k, v) for k, v in g.items() if k.startswith("test_") and callable(v))
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS {name}")
        except Exception as e:  # noqa: BLE001
            failed.append(name)
            print(f"  FAIL {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
