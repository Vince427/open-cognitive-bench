# Global report — Open Cognitive Bench (status 2026-06-04)

A single honest snapshot: what exists, what was tested, what the real-model pilots found, and what is left.
For detail see `PILOT.md` (pilots), `KNOWN_ISSUES.md` (findings V1–V5 + QA log), `CONCEPTUAL_FOUNDATION.md`
(why), `bench/preregistration.md` (the frozen plan + gates), `bench/pilot/README.md` (how to run a real model).

## 1. What this is
Evidence-backed guardrails for AI coding agents, as portable **Skills** + an active **Workflow**, plus a
falsifiable, execution-based **benchmark** that measures whether they help. Five "respect-failure" dimensions:

| Kind | Guardrail | Failure (execution-defined) | Status |
|---|---|---|---|
| chesterton | Chesterton's Shield | breaks a hidden functional invariant | benchmarked-ready |
| goodhart | Goodhart Attack | passes the weak visible test, fails the hidden one | benchmarked-ready |
| hyrum | Hyrum's Shield | changes observable behavior outside the requested scope | **experimental** |
| security | Fail-Safe ("Don't Disarm") | weakens a security control during a refactor | **experimental** |
| phantom | Phantom Check | calls an API/symbol that doesn't exist | **experimental** |

## 2. What is built & green
- **41 trap tasks** (11 dev + 30 held-out), all `selfcheck` VALID (original passes / naive rewrite breaks).
- Harness: `run_bench` (arms B/C/D/S/W, kind→skill, `context_files`), `judge` (execution + CSV export),
  `stats` (McNemar + task-clustered bootstrap + Bonferroni + ASCII forest plot), `power.py` (Monte-Carlo
  power + type-I calibration), `selfcheck`, providers (anthropic/openai/mock), **`bench/pilot/`** (subagent
  runner). **21 harness unit tests.** CI = pure stdlib.
- QA log resolved/*documented*: M1–M4, L1–L4, N1–N4; validity findings V1 (de-spoil), V2 (scope), V3
  (over-spec risk), V4 (experimental-task quality), V5 (construct ceiling — below).

## 3. What was tested on a REAL model (the pilots — `PILOT.md`)
Method: Claude Code **subagents as the model under test** (no API key), single-shot/no-tools (forbidden to
read `hidden_test.py`), exact `run_bench` prompts, scored by the unmodified judge/stats.

| Run | Model | Arms × tasks | Result |
|---|---|---|---|
| Pilot 1 | Opus-class (session) | B/C/D/S × 10 | **0/40 failures — no separation** |
| Pilot 2 | Haiku | B/C/D/S × 10 | **0/40 failures — no separation** |
| Hardening probe | Haiku + Opus | B/S × `split-name` | **all pass** (models avoid the naive unpack) |

Coverage: **all 5 kinds**, arms **B/C/D/S** on two model tiers. **Arm W not run** (4-call workflow; deferred).
Verified non-artifact: bare arms genuinely refactored *and* preserved every trap (spot-checked).

## 4. The headline finding — a construct ceiling (V5)
Toy, single-shot Python refactors **do not discriminate competent models** — not at frontier, not at Haiku,
not on a deliberately harder trap. The guardrails target *not investigating large, unfamiliar code*; but a
single-shot toy task either **shows** the needed fact (trivial) or **withholds** it (unfair) — investigation
is never both possible and necessary. So this construct **cannot** show the guardrails' value for capable
models. The mock's apparent S≫B advantage was an artifact of hard-coded break rates, now falsified by real
behavior.

## 5. Provider choice (yours)
- **API** (`run.ps1`/`run.sh` + key): multi-model, many-seed, scales to the sealed held-out run. Needed for a
  publishable result.
- **Subagents** (`bench/pilot/`): real behavior in-session, no key — but one model, no seeds, pilot-grade.
- **Mock**: plumbing only; never a result.

## 6. Honest limitations (unchanged by the pilots)
Single author (skills + all tasks + harness); toy/likely-memorized tasks; single-shot/no-tools construct
(V2/V5); experimental kinds unvalidated; W is a single-pass stub (M4). A publishable claim needs independent
held-out authorship + a tool-using harness + multi-model runs.

## 7. The agentic follow-up (V2) — built AND run; the result is a caution (`PAPER.md`)
The single-shot ceiling (§4) said the construct had to be agentic, so the tool-using harness was built
(`bench/agentic/`, real repo + git history; fixtures moved out-of-tree after a leakage fix) and run over
rounds 1–4:
- **Misleading-instruction round** ("this is redundant, remove it"): a clean monotonic separation — bare
  **B 5/12**, caution **C 3/12**, skill **S 0/12** (the project's first real arm separation). But p≈0.06 and
  the gap sits on the *null control*, so it is **not significant**.
- **Neutral-instruction round (the decisive control):** the separation **vanishes** — **B 0/12 = S 0/12**.
  Bare agents refactored genuinely and kept every trap.
- **Conclusion:** the skill's measured value is **resistance to a misleading instruction
  (sycophancy-resistance), NOT superior investigation.** With a neutral ask there is no effect.

Still open, in priority order:
1. A *neutral* investigation trap (pressure without the sycophancy confound) + independent fixture/skill
   authorship, ≥2 models, dozens of seeds + the real McNemar/bootstrap stats → fill `RESULTS.md`.
2. Independent held-out authorship for any single-shot regression checks.
3. Validate (or retire) the 3 experimental kinds once a discriminating, neutral harness exists.
4. Keep toy single-shot tasks as plumbing/regression checks only.

> **Superseded note:** an early n=2 Haiku micro-pilot was once described as "bare B 1/2 vs skill S 0/2." The
> scored artifact (`results/pilot-20260604-094001/judgments.jsonl`) shows **B 0/2, S 0/2** — treat the "1/2"
> as anecdotal scratch, not a reproduced result. The reproduced agentic numbers are the round-1–4 ones above.

> Bottom line: the apparatus is sound and produces *real* evidence. That evidence says the single-shot toy
> design can't measure the target construct (§4); the agentic harness *can* produce failures, but the measured
> "skill" effect is **instruction-resistance, not investigation** — under a neutral instruction the gap
> vanishes (B 0/12 = S 0/12). Published per the negative-results-too policy, including the part where the
> original design was the wrong one.
