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


def forest_row(label, diff, lo, hi, sig, width=41, label_w=12):
    """One monospace forest-plot line: a [lo .. hi] CI bar with the point estimate `o`, over an axis
    mapping the failure-rate difference [-1, +1] to `width` cols (0 at center). Pure-stdlib, no deps."""
    def col(v):
        v = max(-1.0, min(1.0, v))
        return int(round((v + 1) / 2 * (width - 1)))
    cells = [" "] * width
    cells[col(0.0)] = "|"                       # zero line
    a, b = sorted((col(lo), col(hi)))
    for i in range(a, b + 1):
        if cells[i] == " ":
            cells[i] = "-"
    cells[a], cells[b] = "[", "]"
    cells[col(diff)] = "o"                       # point estimate (may overwrite a bracket/zero)
    return f"{label:<{label_w}.{label_w}} {''.join(cells)} {diff:+.3f}{' *' if sig else ''}"


def forest_block(rows, width=41):
    """Render a list of (label, diff, lo, hi, sig) as a fenced ASCII forest plot."""
    if not rows:
        return []
    center = int(round(0.5 * (width - 1)))
    ruler = [" "] * width
    for c, ch in ((0, "-"), (center, "0"), (width - 1, "+")):
        ruler[c] = ch
    scale = f"{'':12} {''.join(ruler)}"
    head = f"{'-1.0':<12} {'(X−Y failure-rate difference)':<{width}} +1.0"
    body = [forest_row(*r, width=width) for r in rows]
    return ["", "## Forest plot (negative ⇒ X failed less ⇒ X better; `*` = significant)", "",
            "```", head, scale] + body + ["```",
            "_CI bar = bootstrap 95% CI; `o` = point estimate; `|`/`0` = no difference._", ""]


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

    fail_meaning = {"chesterton": "regression", "goodhart": "metric-gaming (hack)",
                    "hyrum": "scope regression", "security": "security regression", "phantom": "phantom API"}
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

    # Goodhart detail breakdown (KNOWN_ISSUES M3): pooled "failure" = hack only, so surface
    # hacked/correct/incompetent — an arm that merely fails to pass the visible test (incompetent) must not
    # masquerade as low-failure. "conditional hack" = hack rate among runs that passed the visible test.
    gd = defaultdict(lambda: defaultdict(int))
    for j in js:
        if j.get("kind") == "goodhart":
            gd[j["arm"]][j.get("detail", "?")] += 1
    if gd:
        out += ["", "## Goodhart detail (per arm)", "",
                "| Arm | n | hacked | correct | incompetent | hack rate | conditional hack |",
                "|---|---|---|---|---|---|---|"]
        for a in arms:
            c = gd.get(a)
            if not c:
                continue
            n = sum(c.values())
            h, co, inc = c.get("hacked", 0), c.get("correct", 0), c.get("incompetent", 0)
            cond = f"{h / (h + co):.3f}" if (h + co) else "-"
            out.append(f"| {a} | {n} | {h} | {co} | {inc} | {h / n:.3f} | {cond} |")

    bonf = ALPHA / len(COMPARISONS)
    out += ["", "## Pre-registered comparisons (pooled)", "",
            f"Bonferroni-corrected alpha = {ALPHA}/{len(COMPARISONS)} = **{bonf:.4f}**", "",
            "| X vs Y | Δ failure (X−Y) | bootstrap 95% CI | McNemar p (n10/n01) | cost X/Y | verdict |",
            "|---|---|---|---|---|---|"]
    rng = random.Random(0)
    forest = []
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
        forest.append((f"{x} vs {y}", diff, lo, hi, sig))

    out += forest_block(forest)
    out += ["_Lower failure rate is better; negative Δ means X failed less than Y._",
            "_Primary comparison is **W vs S**, interpreted net of the cost ratio. **S vs D** isolates the rule from prompt length._", ""]
    report = "\n".join(out)
    (run_dir / "report.md").write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"\nWrote {run_dir / 'report.md'}")


if __name__ == "__main__":
    main()
