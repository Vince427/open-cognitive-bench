"""Open Cognitive Bench — judge.

Primary metric = EXECUTION: for each produced edit, drop it into an isolated copy of the task and run the
HIDDEN behavior-covering test. A failing test == a regression (the agent broke the invariant).

Uses pytest if it is installed; otherwise falls back to a built-in stdlib test runner (the hidden tests are
plain `assert`-based `test_*` functions, runnable without pytest). So the harness needs NO third-party deps.

Secondary (advisory only): whether the response cited a verifiable artifact (a Fence Report).

Usage:
    python bench/judge.py --run results/latest
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
HAVE_PYTEST = importlib.util.find_spec("pytest") is not None

FENCE_RE = re.compile(r"fence report|invariant to preserve|likely reason it exists", re.IGNORECASE)
CITATION_RE = re.compile(r"commit [0-9a-f]{6,}|git blame|caller|test[_ ]|ticket|OPS-\d+", re.IGNORECASE)


def resolve_run(arg: str) -> Path:
    p = Path(arg)
    if p.is_file():                      # results/latest pointer file
        return Path(p.read_text(encoding="utf-8").strip())
    if p.is_dir():
        return p
    raise SystemExit(f"cannot resolve run: {arg}")


def _run_funcs(workdir: Path, hidden_test: str):
    """Stdlib fallback: import the hidden_test module from workdir and run every test_* function."""
    for m in ("legacy", "hidden_test"):
        sys.modules.pop(m, None)
    sys.path.insert(0, str(workdir))
    fails = []
    try:
        spec = importlib.util.spec_from_file_location("hidden_test", str(workdir / hidden_test))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["hidden_test"] = mod
        spec.loader.exec_module(mod)     # runs `from legacy import ...` against workdir/legacy.py
        for name in sorted(dir(mod)):
            if name.startswith("test_"):
                try:
                    getattr(mod, name)()
                except AssertionError:
                    fails.append(name)
                except Exception as e:   # noqa: BLE001  (import/syntax errors in a bad edit = regression)
                    fails.append(f"{name}<{type(e).__name__}>")
    except Exception as e:               # noqa: BLE001
        fails.append(f"COLLECT<{type(e).__name__}>")
    finally:
        sys.path.remove(str(workdir))
        for m in ("legacy", "hidden_test"):
            sys.modules.pop(m, None)
    return fails


def hidden_test_passes(work: Path, hidden_test: str) -> bool:
    if HAVE_PYTEST:
        try:
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", hidden_test],
                                  cwd=work, capture_output=True, text=True, timeout=120)
            return proc.returncode == 0
        except Exception as e:  # noqa: BLE001
            print(f"    [judge] pytest error: {e}")
            return False
    return len(_run_funcs(work, hidden_test)) == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="results/latest")
    args = ap.parse_args()

    run_dir = resolve_run(args.run)
    records = [json.loads(l) for l in (run_dir / "runs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    work_root = RESULTS / "_work" / run_dir.name
    print(f"[judge] test runner: {'pytest' if HAVE_PYTEST else 'stdlib fallback'}")

    judgments = []
    for rec in records:
        task_dir = Path(rec["task_dir"])
        meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        work = work_root / rec["task_id"] / rec["arm"] / f"seed{rec['seed']}"
        if work.exists():
            shutil.rmtree(work)
        shutil.copytree(task_dir, work)
        (work / rec["target_file"]).write_text(rec["edited_code"], encoding="utf-8")

        passed = hidden_test_passes(work, meta["hidden_test"])
        text = rec.get("response_text", "")
        fence_ok = bool(FENCE_RE.search(text) and CITATION_RE.search(text))
        judgments.append({
            "task_id": rec["task_id"], "arm": rec["arm"], "seed": rec["seed"],
            "regression": (not passed), "fence_report_ok": fence_ok,
            "cost_usd": rec["cost_usd"], "latency_s": rec["latency_s"],
            "input_tokens": rec["input_tokens"], "output_tokens": rec["output_tokens"],
        })
        print(f"  {rec['task_id']:16s} {rec['arm']} seed={rec['seed']} -> {'REGRESSION' if not passed else 'ok'}")

    (run_dir / "judgments.jsonl").write_text(
        "\n".join(json.dumps(j, ensure_ascii=False) for j in judgments) + "\n", encoding="utf-8")
    n_reg = sum(j["regression"] for j in judgments)
    print(f"\nJudged {len(judgments)} runs; {n_reg} regressions -> {run_dir / 'judgments.jsonl'}")


if __name__ == "__main__":
    main()
