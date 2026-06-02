# Pre-registration — Open Cognitive Bench (Chesterton's Shield)

> Fill and **freeze this file (commit it) BEFORE running on the sealed held-out set.** This is the single
> most important defense against tuning a skill to its own benchmark. Dev-set iteration is unrestricted;
> the held-out set is scored exactly once with the values frozen here.

## Hypothesis
A multi-agent cognitive-gating **Workflow (W)** reduces the held-out regression rate relative to a strong
**single-agent + Skill (S)** baseline, on "Chesterton-trap" code-modification tasks.

## Primary metric
**Failure rate** = fraction of (task × seed) runs that FAIL, lower is better. Failure is execution-defined,
per task kind:
- **chesterton**: the produced edit fails the hidden behavior test (regression).
- **goodhart**: the *visible* test passes but the held-out *hidden* test fails (metric-gaming / "hack").
Reported pooled across kinds AND broken down per kind by `stats.py`.

## Arms
B (bare) · C (caution instruction) · D (length/context-matched brief, no rule) · S (Skill) · W (Workflow).

## Comparisons
- **Primary: W vs S** (paired). Direction: W < S. Interpreted **net of the measured cost ratio**.
- **Key isolation: S vs D** — does the Skill beat a length-matched, ruleless brief? If yes, the *rule* is
  the active ingredient, not prompt length. (S/D length parity is auditable via per-arm input tokens.)
- Falsifiers: **S vs B**, **D vs B**, **C vs B**.

## Statistical plan
- Paired **McNemar** exact test on per-(task,seed) pass/fail for each comparison.
- **Bootstrap 95% CI** (1000 resamples, resampling tasks) on the regression-rate difference.
- **Bonferroni** correction across the **5** reported comparisons (α = 0.05 / 5 = **0.01**).
- Decision rule: claim an effect only if its bootstrap CI excludes 0 AND McNemar p < 0.01.

## Construct (what this measures — read with the limits)
Single-shot, no-tools: one prompt in, one edited file out. For chesterton tasks the prompt also carries a
read-only `usage.py` (a caller) so the invariant is **discoverable from usage, not stated in a comment**.
This is a **prompt/skill effect under one-shot conditions**, NOT a tool-using investigative loop (no
`git blame`, no repo grep, no command execution). An agentic harness is out of scope here. See
`README.md` → "What is actually measured" and `KNOWN_ISSUES.md` V1/V2.

## Sample size — PROPOSED defaults (confirm & FREEZE before the held-out run)
- Held-out tasks N = **30** (in repo now: 18 chesterton + 12 goodhart, all selfcheck-validated) ;
  seeds per arm = **5** ; models = **two** (one frontier + one mid-tier, reported separately).
- That yields ≥ 30 × 5 = 150 datapoints per arm per model. Justification: CLT CIs are unreliable below
  ~100 datapoints; if tasks stay scarce, lean on the bootstrap CIs above rather than normal-approx CIs.
- **Power (from `bench/power.py`, mirroring the exact decision rule):** at 30×5, **S vs D** and the
  vs-B falsifiers are well powered (≈90–100%), but the **primary W vs S** is **under-powered for a small
  ~0.10 absolute gap** (~40% power). Decision: report W-vs-S **as a difference + bootstrap CI** (not a
  binary verdict) at this N; if a tight verdict is needed, pre-commit to expanding tasks/seeds (the
  clustered bootstrap benefits more from added **tasks** than added seeds). See `bench/power_analysis.md`.

## Cost reporting (mandatory, not a gate)
Report mean tokens, USD, and wall-clock latency per arm. The W-vs-S verdict is interpreted **net of the
measured cost multiplier** (expected ~5–10× for W before Sherlock-style selective verification).

## Decoding / reproducibility
- Temperature = **0.7** (proposed; confirm) ; seeds recorded ; provider + model versions recorded in `results/<run>/meta.json`.

## Anti-contamination
- Held-out tasks authored by `<a person OTHER than the skill author>`.
- Prefer tasks whose invariants/domains post-date model cutoffs.
- Manually spot-check a sample of "passing" diffs for plausible-but-wrong solutions.

## Publication commitment
Results are published **regardless of outcome**, including W not beating S or the cost not being justified.
