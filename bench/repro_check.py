#!/usr/bin/env python3
"""Reproducibility gate: run the deterministic mock pipeline twice and assert the
*scientifically meaningful* outputs are identical.

Why normalize instead of a raw byte-diff: the pipeline embeds two legitimately
non-deterministic things that must NOT fail the gate ---
  * judgments.jsonl: `latency_s` is a measured wall-clock time (varies run to run);
  * report.md: the `Run: run-<timestamp>` header carries the run-id timestamp.
Everything else (verdicts, cost, tokens, and every statistic McNemar/bootstrap derives)
is deterministic given the seeded mock provider, so we strip the two volatile fields and
compare the rest exactly.

This is a *reproducibility* check (does the measurement pipeline reproduce on identical
inputs?), NOT a claim that real-model runs are deterministic (they never are -- keep those
out of this gate). Exit 0 = reproducible, 1 = drift detected.
"""
from __future__ import annotations

import glob
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOLATILE_JUDGMENT_KEYS = {"latency_s"}          # measured timing -- non-deterministic by nature
RUN_ID_PREFIX = "Run:"                            # the report.md header line carrying the timestamp


def run_pipeline() -> Path:
    """Run mock bench -> judge -> stats once; return the new results/run-* directory."""
    before = set(glob.glob(str(REPO / "results" / "run-*")))
    subprocess.run(
        [sys.executable, "bench/run_bench.py", "--tasks", "bench/tasks/dev",
         "--arms", "B", "C", "D", "S", "W", "--seeds", "5", "--provider", "mock"],
        cwd=REPO, check=True, stdout=subprocess.DEVNULL,
    )
    after = set(glob.glob(str(REPO / "results" / "run-*")))
    new = sorted(after - before)
    if not new:
        sys.exit("repro_check: run_bench produced no new results/run-* directory")
    run_dir = Path(new[-1])
    subprocess.run([sys.executable, "bench/judge.py", "--run", str(run_dir)],
                   cwd=REPO, check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "bench/stats.py", "--run", str(run_dir)],
                   cwd=REPO, check=True, stdout=subprocess.DEVNULL)
    return run_dir


def normalized_judgments(run_dir: Path) -> list[dict]:
    rows = []
    for line in (run_dir / "judgments.jsonl").read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        obj = {k: v for k, v in json.loads(line).items() if k not in VOLATILE_JUDGMENT_KEYS}
        rows.append(obj)
    # Sort so output ordering can't introduce a false diff; the key set is stable per record.
    rows.sort(key=lambda o: json.dumps(o, sort_keys=True))
    return rows


def normalized_report(run_dir: Path) -> list[str]:
    return [ln for ln in (run_dir / "report.md").read_text().splitlines()
            if not ln.strip().startswith(RUN_ID_PREFIX)]


def main() -> int:
    a, b = run_pipeline(), run_pipeline()
    print(f"repro_check: comparing {a.name} vs {b.name}")

    ok = True
    if normalized_judgments(a) != normalized_judgments(b):
        ok = False
        print("DRIFT: judgments differ (after stripping latency_s) -- the verdict/cost/token "
              "pipeline is non-deterministic.")
    if normalized_report(a) != normalized_report(b):
        ok = False
        print("DRIFT: report.md statistics differ (after stripping the run-id header) -- "
              "stats.py is non-deterministic on identical inputs.")

    if ok:
        print("OK: the mock pipeline reproduces -- verdicts, costs, tokens, and all statistics "
              "are identical across two runs (only timing/timestamp vary, as expected).")
        return 0
    print("Reproducibility gate FAILED. A hidden source of non-determinism crept in "
          "(dict/set ordering, time, file globbing, unseeded RNG, float drift).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
