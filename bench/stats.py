"""Open Cognitive Bench — statistics (pure stdlib, no numpy/scipy required).

Reads judgments.jsonl and computes, for the pre-registered comparisons (W vs S, S vs D, S vs B, D vs B, C vs B):
  - per-arm FAILURE rate (regression for chesterton tasks; metric-gaming/"hack" for goodhart tasks),
  - a by-kind breakdown (so the two guardrail dimensions are reported separately),
  - paired McNemar EXACT test (two-sided binomial on discordant pairs),
  - bootstrap 95% CI on the failure-rate difference (resampling TASKS, to respect clustering),
  - Bonferroni-corrected alpha.

Writes results/<run>/report.md and prints it.

Usage:
    python bench/stats.py --run results/latest
"""
from __future__ import annotations
import argparse
import json
import random
import sys
from collections import defaultdict
from math import comb
from pathlib import Path

# Primary: W vs S. Key isolation: S vs D (rule vs mere prompt length). Falsifiers: S/D/C vs B.
COMPARISONS = [("W", "S"), ("S", "D"), ("S", "B"), ("D", "B"), ("C", "B")]
N_BOOT = 1000
ALPHA = 0.05


def resolve_run(arg: str) -> Path:
    p = Path(arg)
    if p.is_file():
        return Path(p.read_text(encoding="utf-8").strip())
    if p.is_dir():
        return p
    raise SystemExit(f"cannot resolve run: {arg}")


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def mcnemar_exact(x, y, keys):
    n10 = sum(1 for k in keys if x[k] == 1 and y[k] == 0)
    n01 = sum(1 for k in keys if x[k] == 0 and y[k] == 1)
    n = n10 + n01
    if n == 0:
        return n10, n01, 1.0
    k = min(n10, n01)
    tail = sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return n10, n01, min(1.0, 2.0 * tail)


def percentile(vals, q):
    if not vals:
        return float("nan")
    idx = int(round(q / 100.0 * (len(vals) - 1)))
    return vals[max(0, min(len(vals) - 1, idx))]


def bootstrap_diff_ci(x, y, keys, rng):
    by_task = defaultdict(list)
    for (task, seed) in keys:
        by_task[task].append((task, seed))
    tasks = list(by_task)
    diffs = []
    for _ in range(N_BOOT):
        sampled = [tasks[rng.randrange(len(tasks))] for _ in tasks]
        xk, yk = [], []
        for t in sampled:
            for key in by_task[t]:
                xk.append(x[key]); yk.append(y[key])
        diffs.append(mean(xk) - mean(yk))
    diffs.sort()
    return percentile(diffs, 2.5), percentile(diffs, 97.5)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="results/latest")
    args = ap.parse_args()
    run_dir = resolve_run(args.run)
    js = [json.loads(l) for l in (run_dir / "judgments.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

    arms = sorted({j["arm"] for j in js})
    kinds = sorted({j.get("kind", "chesterton") for j in js})
    reg = {a: {} for a in arms}                      # pooled failure, keyed (task,seed)
    by_kind = defaultdict(lambda: defaultdict(list))  # by_kind[kind][arm] -> [failed...]
    cost, lat, tok, art = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    for j in js:
        f = 1 if j["failed"] else 0
        reg[j["arm"]][(j["task_id"], j["seed"])] = f
        by_kind[j.get("kind", "chesterton")][j["arm"]].append(f)
        cost[j["arm"]].append(j["cost_usd"]); lat[j["arm"]].append(j["latency_s"])
        tok[j["arm"]].append(j["input_tokens"] + j["output_tokens"])
        art[j["arm"]].append(1 if j.get("artifact_ok") else 0)

    fail_meaning = {"chesterton": "regression", "goodhart": "metric-gaming (hack)"}
    out = ["# Open Cognitive Bench — report", "", f"Run: `{run_dir.name}`",
           f"Task kinds: {', '.join(k + ' = ' + fail_meaning.get(k, k) for k in kinds)}", "",
           "## Per-arm summary (failure rate, pooled across kinds)", "",
           "| Arm | n | Failure rate | Artifact-cited | Mean $/run | Mean tokens | Mean latency (s) |",
           "|---|---|---|---|---|---|---|"]
    cost_by_arm = {}
    for a in arms:
        cost_by_arm[a] = mean(cost[a])
        out.append(f"| {a} | {len(reg[a])} | {mean(reg[a].values()):.3f} | {mean(art[a]):.2f} | "
                   f"${cost_by_arm[a]:.4f} | {mean(tok[a]):.0f} | {mean(lat[a]):.3f} |")

    if len(kinds) > 1:
        out += ["", "## By task kind (failure rate per arm)", "",
                "| Kind (failure = ) | " + " | ".join(arms) + " |",
                "|" + "---|" * (len(arms) + 1)]
        for k in kinds:
            cells = " | ".join(f"{mean(by_kind[k][a]):.3f}" if by_kind[k][a] else "-" for a in arms)
            out.append(f"| {k} ({fail_meaning.get(k, k)}) | {cells} |")

    bonf = ALPHA / len(COMPARISONS)
    out += ["", "## Pre-registered comparisons (pooled)", "",
            f"Bonferroni-corrected alpha = {ALPHA}/{len(COMPARISONS)} = **{bonf:.4f}**", "",
            "| X vs Y | Δ failure (X−Y) | bootstrap 95% CI | McNemar p (n10/n01) | cost X/Y | verdict |",
            "|---|---|---|---|---|---|"]
    rng = random.Random(0)
    for x, y in COMPARISONS:
        if x not in reg or y not in reg:
            continue
        keys = [k for k in reg[x] if k in reg[y]]
        if not keys:
            continue
        diff = mean(reg[x][k] for k in keys) - mean(reg[y][k] for k in keys)
        lo, hi = bootstrap_diff_ci(reg[x], reg[y], keys, rng)
        n10, n01, p = mcnemar_exact(reg[x], reg[y], keys)
        ratio = (cost_by_arm[x] / cost_by_arm[y]) if cost_by_arm.get(y) else float("inf")
        sig = (hi < 0 or lo > 0) and p < bonf
        verdict = ("X better" if diff < 0 else "Y better") if sig else "no sig. effect"
        out.append(f"| {x} vs {y} | {diff:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {p:.4f} ({n10}/{n01}) | {ratio:.1f}× | {verdict} |")

    out += ["", "_Lower failure rate is better; negative Δ means X failed less than Y._",
            "_Primary comparison is **W vs S**, interpreted net of the cost ratio. **S vs D** isolates the rule from prompt length._", ""]
    report = "\n".join(out)
    (run_dir / "report.md").write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"\nWrote {run_dir / 'report.md'}")


if __name__ == "__main__":
    main()
