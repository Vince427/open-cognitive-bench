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

## 7. Next, in priority order
1. **Build the agentic, tool-using harness (V2)** — the only setting where these guardrails can bite (real
   repo, git history, callers, run-tests; skill gates whether the agent investigates). Needs a live model.
2. Independent held-out authorship; then a multi-model API run → fill `RESULTS.md`.
3. Validate (or retire) the 3 experimental kinds once a discriminating harness exists.
4. Keep toy single-shot tasks as plumbing/regression checks only.

> Bottom line: the apparatus is sound and now produces *real* evidence — and that evidence says the current
> (single-shot, toy) design can't measure the thing we care about. That redirect is the most useful result so
> far, and it is published here per the project's negative-results-too policy.
