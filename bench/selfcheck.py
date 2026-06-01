"""Stdlib-only self-check (no numpy/scipy/pytest needed).

Validates that every benchmark task is a VALID trap:
  - the ORIGINAL legacy code PASSES its hidden test (the code is correct, merely ugly), and
  - the naive BAD rewrite (from providers.BAD_REWRITES) FAILS the hidden test (the trap actually bites).

Run with any Python 3.9+:
    python bench/selfcheck.py
Exit code 0 if all tasks are valid traps, 1 otherwise.
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

BENCH = Path(__file__).resolve().parent
ROOT = BENCH.parent
sys.path.insert(0, str(BENCH))
from providers import BAD_REWRITES  # noqa: E402


def run_hidden_tests(dirpath: Path):
    """Import the task's hidden_test from dirpath and run every test_* function. Return list of failures."""
    for m in ("legacy", "hidden_test"):
        sys.modules.pop(m, None)
    sys.path.insert(0, str(dirpath))
    failures = []
    try:
        import hidden_test  # resolves legacy from dirpath (sys.path[0])
        for name in sorted(dir(hidden_test)):
            if name.startswith("test_"):
                try:
                    getattr(hidden_test, name)()
                except AssertionError:
                    failures.append(name)
                except Exception as e:  # noqa: BLE001
                    failures.append(f"{name}<{type(e).__name__}: {e}>")
    finally:
        sys.path.remove(str(dirpath))
        for m in ("legacy", "hidden_test"):
            sys.modules.pop(m, None)
    return failures


def main():
    tasks = sorted((ROOT / "bench" / "tasks").rglob("task.json"))
    ok = True
    print(f"{'task':18s} {'original':18s} {'naive-rewrite':18s} verdict")
    print("-" * 70)
    for tj in tasks:
        meta = json.loads(tj.read_text(encoding="utf-8"))
        tdir = tj.parent
        orig_fail = run_hidden_tests(tdir)
        original_ok = (len(orig_fail) == 0)

        # naive rewrite variant
        bad_ok_label = "n/a"
        trap_bites = True
        if meta["id"] in BAD_REWRITES:
            with tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                (tmp / meta["target_file"]).write_text(BAD_REWRITES[meta["id"]], encoding="utf-8")
                (tmp / meta["hidden_test"]).write_text((tdir / meta["hidden_test"]).read_text(encoding="utf-8"), encoding="utf-8")
                bad_fail = run_hidden_tests(tmp)
            trap_bites = (len(bad_fail) > 0)
            bad_ok_label = "FAILS (good)" if trap_bites else "PASSES (!!)"
        else:
            bad_ok_label = "no bad-rewrite"

        valid = original_ok and trap_bites
        ok = ok and valid
        print(f"{meta['id']:18s} {('PASS' if original_ok else 'FAIL ' + str(orig_fail)):18s} {bad_ok_label:18s} {'VALID TRAP' if valid else 'INVALID'}")

    print("-" * 70)
    print("ALL TASKS VALID" if ok else "SOME TASKS INVALID")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
