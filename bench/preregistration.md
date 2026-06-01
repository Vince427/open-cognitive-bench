# Pre-registration — Open Cognitive Bench (Chesterton's Shield)

> Fill and **freeze this file (commit it) BEFORE running on the sealed held-out set.** This is the single
> most important defense against tuning a skill to its own benchmark. Dev-set iteration is unrestricted;
> the held-out set is scored exactly once with the values frozen here.

## Hypothesis
A multi-agent cognitive-gating **Workflow (W)** reduces the held-out regression rate relative to a strong
**single-agent + Skill (S)** baseline, on "Chesterton-trap" code-modification tasks.

## Primary metric
**Regression rate** = fraction of (task × seed) runs whose produced edit FAILS the task's hidden,
behavior-covering test (`hidden_test`). Lower is better.

## Primary comparison
**W vs S** (paired, same tasks/seeds). Direction: W < S.
Falsifier arms reported but not primary: **S vs B** (skill vs nothing), **C vs B** (skill vs mere caution).

## Statistical plan
- Paired **McNemar** test on per-(task,seed) pass/fail for W vs S.
- **Bootstrap 95% CI** (1000 resamples, resampling tasks) on the regression-rate difference for W−S, S−B, C−B.
- **Bonferroni** correction across the 3 reported comparisons (α = 0.05 → 0.0167).
- Decision rule: claim an effect only if the W−S bootstrap CI excludes 0 AND McNemar p < 0.0167.

## Sample size (FREEZE before the held-out run)
- Held-out tasks N = `<fill, target ≥ 30>` ; seeds per arm = `<fill, ≥ 5>` ; models = `<fill, e.g. one frontier + one mid>`.
- Justification: CLT CIs are unreliable below ~100 datapoints; N_tasks × seeds should reach the low hundreds,
  else rely on the bootstrap/Bayesian intervals reported above.

## Cost reporting (mandatory, not a gate)
Report mean tokens, USD, and wall-clock latency per arm. The W-vs-S verdict is interpreted **net of the
measured cost multiplier** (expected ~5–10× for W before Sherlock-style selective verification).

## Decoding / reproducibility
- Temperature = `<fill>` ; seeds recorded ; provider + model versions recorded in `results/<run>/meta.json`.

## Anti-contamination
- Held-out tasks authored by `<a person OTHER than the skill author>`.
- Prefer tasks whose invariants/domains post-date model cutoffs.
- Manually spot-check a sample of "passing" diffs for plausible-but-wrong solutions.

## Publication commitment
Results are published **regardless of outcome**, including W not beating S or the cost not being justified.
