"""Open Cognitive Bench -- power analysis (pure stdlib, no numpy/scipy, NO LLM).

Question: with the pre-registered design (N tasks x S seeds, paired), what effect size is detectable at
the Bonferroni-corrected alpha? This is the "is the design adequately powered BEFORE we spend on a real
run" check (KNOWN_ISSUES PA).

It does NOT guess what real models will do. It asks: IF the true per-arm failure rates were such-and-such,
how often would our exact decision procedure declare a significant effect? "Power" here is the probability
of a correct rejection.

Faithful to the real pipeline: it reuses `stats.mcnemar_exact` and `stats.bootstrap_diff_ci` and applies the
SAME decision rule as `stats.py` / `preregistration.md`:

    significant  <=>  (bootstrap 95% CI on the failure-rate difference excludes 0)  AND  (McNemar p < bonf)

with bonf = alpha / n_comparisons = 0.05 / 5 = 0.01.

Generative model (paired, with task-level clustering so the bootstrap behaves realistically):
  - each task t draws a random effect b_t ~ Normal(0, sigma) on the logit scale, SHARED by both arms
    (this is what makes the pair correlated and clusters the seeds within a task);
  - arm X fails with prob sigmoid(logit(mX) + b_t), arm Y with sigmoid(logit(mY) + b_t);
  - each (task, seed) is an independent Bernoulli draw from those per-task probabilities.
sigma = task heterogeneity. sigma=0 is the optimistic i.i.d. case; sigma>0 (tasks differ in how often they
trip an arm) shrinks the EFFECTIVE sample size for the task-clustered bootstrap, so power drops -- which is
exactly why the bootstrap clusters by task and why we report a couple of sigma values.

Usage:
    python bench/power.py                 # headline scenarios + MDE table (deterministic)
    python bench/power.py --quick         # fewer sims/resamples (fast; for CI / a quick look)
    python bench/power.py --out bench/power_analysis.md
"""
from __future__ import annotations
import argparse
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats  # noqa: E402  (reuse the SAME mcnemar_exact + bootstrap_diff_ci the real report uses)

ALPHA = 0.05
N_COMPARISONS = 5            # matches stats.COMPARISONS / preregistration
BONF = ALPHA / N_COMPARISONS  # 0.01


def _logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def simulate_once(mX, mY, n_tasks, n_seeds, sigma, rng):
    """One simulated paired experiment. Returns (reg_x, reg_y, keys, realized_mX, realized_mY)."""
    reg_x, reg_y, keys = {}, {}, []
    lX, lY = _logit(mX), _logit(mY)
    sx = sy = 0
    for t in range(n_tasks):
        b = rng.gauss(0.0, sigma) if sigma > 0 else 0.0
        pX, pY = _sigmoid(lX + b), _sigmoid(lY + b)
        for s in range(n_seeds):
            k = (f"task{t}", s)
            fx = 1 if rng.random() < pX else 0
            fy = 1 if rng.random() < pY else 0
            reg_x[k], reg_y[k] = fx, fy
            keys.append(k)
            sx += fx; sy += fy
    n = n_tasks * n_seeds
    return reg_x, reg_y, keys, sx / n, sy / n


def power_for(mX, mY, n_tasks, n_seeds, sigma, sims, rng):
    """Fraction of simulated experiments where the exact decision rule declares X<Y significant.
    Also returns the realized mean failure rates (center rates differ slightly under sigma>0)."""
    hits = 0
    rmX = rmY = 0.0
    for _ in range(sims):
        reg_x, reg_y, keys, ax, ay = simulate_once(mX, mY, n_tasks, n_seeds, sigma, rng)
        rmX += ax; rmY += ay
        diff = ax - ay
        _, _, p = stats.mcnemar_exact(reg_x, reg_y, keys)
        lo, hi = stats.bootstrap_diff_ci(reg_x, reg_y, keys, rng)
        sig = (hi < 0 or lo > 0) and p < BONF
        if sig and diff < 0:          # correct-direction rejection (X fails less than Y)
            hits += 1
    return hits / sims, rmX / sims, rmY / sims


def fmt_pct(x):
    return f"{100 * x:4.1f}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", type=int, default=30, help="held-out task count (default 30)")
    ap.add_argument("--seeds", type=int, default=5, help="seeds per arm (default 5)")
    ap.add_argument("--sims", type=int, default=600, help="Monte-Carlo experiments per scenario")
    ap.add_argument("--boot", type=int, default=400, help="bootstrap resamples per experiment")
    ap.add_argument("--sigmas", type=float, nargs="+", default=[0.0, 1.0],
                    help="task-heterogeneity SDs (logit scale) to report")
    ap.add_argument("--seed", type=int, default=0, help="RNG seed (deterministic output)")
    ap.add_argument("--quick", action="store_true", help="fast preset (sims=200, boot=200)")
    ap.add_argument("--out", default=None, help="also write the markdown report to this path")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if args.quick:
        args.sims, args.boot = 200, 200
    stats.N_BOOT = args.boot           # the reused bootstrap reads this module global
    rng = random.Random(args.seed)

    N, S = args.tasks, args.seeds
    out = [
        "# Open Cognitive Bench -- power analysis",
        "",
        f"Design: **{N} tasks x {S} seeds = {N * S} paired datapoints** per comparison. "
        f"Decision rule (as pre-registered): bootstrap 95% CI excludes 0 AND McNemar p < "
        f"alpha/{N_COMPARISONS} = **{BONF:.4f}**.",
        "",
        f"Monte-Carlo: {args.sims} simulated experiments/scenario, {args.boot} bootstrap resamples each, "
        f"seed={args.seed}. `sigma` = per-task heterogeneity on the logit scale (0 = i.i.d.; larger = tasks "
        "differ more, which the task-clustered bootstrap rightly penalizes). **Power = P(correct rejection)**; "
        "the failure rates below are *assumed* values for a what-if, NOT predictions about real models.",
        "",
        "## Headline scenarios",
        "",
        "Rates use the mock's illustrative pattern (B 0.85 / C 0.65 / D 0.55 / S 0.20 / W 0.10) purely as a "
        "plausible what-if; the real run replaces them with measured rates.",
        "",
        "| Comparison | assumed X (better) | assumed Y | Δ | " +
        " | ".join(f"power σ={s:g}" for s in args.sigmas) + " |",
        "|---|---|---|---|" + "---|" * len(args.sigmas),
    ]
    scenarios = [
        ("W vs S (primary)", "W", 0.10, "S", 0.20),
        ("S vs D (rule vs length)", "S", 0.20, "D", 0.55),
        ("S vs B (skill vs floor)", "S", 0.20, "B", 0.85),
        ("D vs B (length vs floor)", "D", 0.55, "B", 0.85),
        ("C vs B (caution vs floor)", "C", 0.65, "B", 0.85),
    ]
    for label, xn, mX, yn, mY in scenarios:
        cells = []
        for sg in args.sigmas:
            pw, _, _ = power_for(mX, mY, N, S, sg, args.sims, rng)
            cells.append(fmt_pct(pw))
        out.append(f"| {label} | {xn} {mX:.2f} | {yn} {mY:.2f} | {mX - mY:+.2f} | " + " | ".join(cells) + " |")

    # Minimum detectable effect: smallest absolute reduction from a baseline that reaches >=80% power.
    out += [
        "",
        "## Minimum detectable effect (MDE) at 80% power",
        "",
        "Smallest absolute failure-rate reduction from each baseline that this design detects with >=80% "
        "power (grid step 0.05). `>0.X` means even the largest tested reduction did not reach 80% power.",
        "",
        "| Baseline rate | " + " | ".join(f"MDE σ={s:g}" for s in args.sigmas) + " |",
        "|---|" + "---|" * len(args.sigmas),
    ]
    for base in (0.30, 0.40, 0.50, 0.60):
        cells = []
        for sg in args.sigmas:
            mde = None
            red = 0.05
            while round(base - red, 4) >= 0.0 and red <= base:
                pw, _, _ = power_for(base - red, base, N, S, sg, max(args.sims // 2, 120), rng)
                if pw >= 0.80:
                    mde = red
                    break
                red = round(red + 0.05, 4)
            cells.append(f"{mde:.2f}" if mde is not None else f">{base - 0.05:.2f}")
        out.append(f"| {base:.2f} | " + " | ".join(cells) + " |")

    out += [
        "",
        "## How to read this",
        "",
        "- A power below ~80% for a scenario means: *if* the true gap were that size, we'd often FAIL to "
        "call it significant -- the run would be underpowered for that effect.",
        "- The **primary W-vs-S** comparison is the one to watch: a small absolute gap (e.g. 0.20 -> 0.10) on "
        "30x5 is the hardest to detect, especially once task heterogeneity (σ>0) is allowed for. If its power "
        "is low, the honest move is more tasks/seeds (or to report it as a CI, not a verdict).",
        "- Large gaps (S vs B, D vs B) are detected easily; the design's binding constraint is the "
        "small-gap comparisons (W vs S, and W vs D if added).",
        "- Increasing **tasks** helps the clustered bootstrap more than increasing **seeds** (the bootstrap "
        "resamples tasks). Re-run with `--tasks`/`--seeds` to size a follow-up.",
        "",
    ]
    report = "\n".join(out)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
