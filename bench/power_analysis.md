# Open Cognitive Bench -- power analysis

Design: **30 tasks x 5 seeds = 150 paired datapoints** per comparison. Decision rule (as pre-registered): bootstrap 95% CI excludes 0 AND McNemar p < alpha/5 = **0.0100**.

Monte-Carlo: 600 simulated experiments/scenario, 400 bootstrap resamples each, seed=0. `sigma` = per-task heterogeneity on the logit scale (0 = i.i.d.; larger = tasks differ more, which the task-clustered bootstrap rightly penalizes). **Power = P(correct rejection)**; the failure rates below are *assumed* values for a what-if, NOT predictions about real models.

## Headline scenarios

Rates use the mock's illustrative pattern (B 0.85 / C 0.65 / D 0.55 / S 0.20 / W 0.10) purely as a plausible what-if; the real run replaces them with measured rates.

| Comparison | assumed X (better) | assumed Y | Δ | power σ=0 | power σ=1 |
|---|---|---|---|---|---|
| W vs S (primary) | W 0.10 | S 0.20 | -0.10 | 39.0% | 42.5% |
| S vs D (rule vs length) | S 0.20 | D 0.55 | -0.35 | 100.0% | 100.0% |
| S vs B (skill vs floor) | S 0.20 | B 0.85 | -0.65 | 100.0% | 100.0% |
| D vs B (length vs floor) | D 0.55 | B 0.85 | -0.30 | 100.0% | 99.5% |
| C vs B (caution vs floor) | C 0.65 | B 0.85 | -0.20 | 89.5% | 89.2% |

## Minimum detectable effect (MDE) at 80% power

Smallest absolute failure-rate reduction from each baseline that this design detects with >=80% power (grid step 0.05). `>0.X` means even the largest tested reduction did not reach 80% power.

| Baseline rate | MDE σ=0 | MDE σ=1 |
|---|---|---|
| 0.30 | 0.20 | 0.20 |
| 0.40 | 0.20 | 0.20 |
| 0.50 | 0.20 | 0.25 |
| 0.60 | 0.25 | 0.25 |

## Null calibration (type-I error)

With NO true effect (mX = mY), the rule should declare a significant difference at most ~0.01 of the time. Empirical false-positive rate (any direction):

| Baseline rate | FPR σ=0 | FPR σ=1 |
|---|---|---|
| 0.30 |  0.7% |  0.3% |
| 0.50 |  0.8% |  0.8% |

Stays at/below the 0.01 target across heterogeneity levels (±MC noise) — the conservative task-clustered bootstrap in the AND-rule absorbs the McNemar pooling's anticonservatism, so the pre-registered procedure does not inflate false positives under clustering.

> The table above uses the default `--sigmas 0 1`. Calibration was also checked at **σ=1.5** (`power.py --sigmas 0 1 1.5`): FPR stays ≤0.01 there too — this is the "σ up to 1.5" cited in `preregistration.md`.

## How to read this

- A power below ~80% for a scenario means: *if* the true gap were that size, we'd often FAIL to call it significant -- the run would be underpowered for that effect.
- The **primary W-vs-S** comparison is the one to watch: a small absolute gap (e.g. 0.20 -> 0.10) on 30x5 is the hardest to detect, especially once task heterogeneity (σ>0) is allowed for. If its power is low, the honest move is more tasks/seeds (or to report it as a CI, not a verdict).
- Large gaps (S vs B, D vs B) are detected easily; the design's binding constraint is the small-gap comparisons (W vs S, and W vs D if added).
- Increasing **tasks** helps the clustered bootstrap more than increasing **seeds** (the bootstrap resamples tasks). Re-run with `--tasks`/`--seeds` to size a follow-up.

