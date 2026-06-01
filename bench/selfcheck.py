"""Stdlib-only self-check (no numpy/scipy/pytest needed).

Validates that every benchmark task is a VALID trap:
  chesterton: the ORIGINAL code PASSES its hidden test, and the naive BAD rewrite (providers.BAD_REWRITES)
              FAILS it.
  goodhart:   the CORRECT impl (providers.GOODHART_IMPLS) PASSES visible AND hidden tests, while the HACKED
              impl PASSES the visible test but FAILS the hidden one (i.e. the weak test is genuinely gameable).

Run with any Python 3.9+:   python bench/selfcheck.py
Exit code 0 if all tasks are valid traps, 1 otherwise.
"""
from __future__ import annotations
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

BENCH = Path(__file__).resolve().parent
ROOT = BENCH.parent
sys.path.insert(0, str(BENCH))
from providers import BAD_REWRITES, GOODHART_IMPLS  # noqa: E402


def run_test_file(dirpath: Path, test_file: str):
    """Import a test module from dirpath and run every test_* function. Return list of failures."""
    modname = Path(test_file).stem
    for m in ("legacy", "hidden_test", "visible_test"):
        sys.modules.pop(m, None)
    sys.path.insert(0, str(dirpath))
    fails = []
    try:
        spec = importlib.util.spec_from_file_location(modname, str(Path(dirpath) / test_file))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod
        spec.loader.exec_module(mod)
        for name in sorted(dir(mod)):
            if name.startswith("test_"):
                try:
                    getattr(mod, name)()
                except AssertionError:
                    fails.append(name)
                except Exception as e:  # noqa: BLE001
                    fails.append(f"{name}<{type(e).__name__}>")
    except Exception as e:  # noqa: BLE001
        fails.append(f"COLLECT<{type(e).__name__}>")
    finally:
        sys.path.remove(str(dirpath))
        for m in ("legacy", modname):
            sys.modules.pop(m, None)
    return fails


def _write(tmp: Path, name: str, content: str):
    (tmp / name).write_text(content, encoding="utf-8")


def check_chesterton(meta, tdir):
    original_ok = (len(run_test_file(tdir, meta["hidden_test"])) == 0)
    trap_bites, c2 = True, "no bad-rewrite"
    if meta["id"] in BAD_REWRITES:
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            _write(t, meta["target_file"], BAD_REWRITES[meta["id"]])
            _write(t, meta["hidden_test"], (tdir / meta["hidden_test"]).read_text(encoding="utf-8"))
            trap_bites = len(run_test_file(t, meta["hidden_test"])) > 0
        c2 = "naive FAILS (good)" if trap_bites else "naive PASSES (!!)"
    return ("orig PASS" if original_ok else "orig FAIL"), c2, (original_ok and trap_bites)


def check_goodhart(meta, tdir):
    impls = GOODHART_IMPLS.get(meta["id"])
    if not impls:
        return "no impls", "no impls", False
    vis, hid = meta["visible_test"], meta["hidden_test"]
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        _write(t, vis, (tdir / vis).read_text(encoding="utf-8"))
        _write(t, hid, (tdir / hid).read_text(encoding="utf-8"))
        _write(t, meta["target_file"], impls["correct"])
        correct_ok = (len(run_test_file(t, vis)) == 0) and (len(run_test_file(t, hid)) == 0)
        _write(t, meta["target_file"], impls["hacked"])
        hacked_games = (len(run_test_file(t, vis)) == 0) and (len(run_test_file(t, hid)) > 0)
    return ("correct PASS" if correct_ok else "correct FAIL"), \
           ("hacked GAMES (good)" if hacked_games else "hacked caught/broke (!!)"), (correct_ok and hacked_games)


def main():
    tasks = sorted((ROOT / "bench" / "tasks").rglob("task.json"))
    ok = True
    print(f"{'task':18s} {'kind':11s} {'check 1':16s} {'check 2':22s} verdict")
    print("-" * 84)
    for tj in tasks:
        meta = json.loads(tj.read_text(encoding="utf-8"))
        kind = meta.get("kind", "chesterton")
        if kind == "goodhart":
            c1, c2, valid = check_goodhart(meta, tj.parent)
        else:
            c1, c2, valid = check_chesterton(meta, tj.parent)
        ok = ok and valid
        print(f"{meta['id']:18s} {kind:11s} {c1:16s} {c2:22s} {'VALID TRAP' if valid else 'INVALID'}")
    print("-" * 84)
    print("ALL TASKS VALID" if ok else "SOME TASKS INVALID")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
