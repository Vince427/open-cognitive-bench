# Pilot run — real model behavior via Claude Code subagents (DEV set)

> **This is NOT the pre-registered held-out result** (see `RESULTS.md` for that, still pending). It is a
> first **real-model** pilot that replaces the tautological `--provider mock` with actual model attempts, to
> run the **dev-set separation gate** in `bench/preregistration.md`. Date: 2026-06-04.

## Why
The harness was only ever exercised by the deterministic `mock` provider (hard-coded break rates — tautological).
But Claude Code can spawn **subagents that are real models**. So we used a fresh subagent as the "model under
test" for each (task, arm) cell — real behavior, execution-judged — without needing an external API key.

## Method (reproducible)
1. `results/_pilot/gen.py` builds the **exact** prompt `run_bench` would send for each (task, arm), using
   `run_bench.system_for` + `base_user` (arm S gets the real `SKILL.md`; C the matched caution; D the
   length brief; B nothing), and writes one prompt file per cell.
2. One subagent per cell (general-purpose), instructed to act as the model under test, **single-shot and
   no-tools**: read ONLY its prompt file, produce the edited file, write it out. Explicitly forbidden to read
   any other file (so it cannot peek at `hidden_test.py`), run commands, or investigate — faithful to the
   benchmark's single-shot construct (`KNOWN_ISSUES.md` V2).
3. `results/_pilot/assemble.py` collects the edits into a `run_bench`-format run dir; the **unmodified**
   `bench/judge.py` + `bench/stats.py` score them by execution.

## Scope & caveats (read before quoting any number)
- **One model** — the session's frontier model (Claude, Opus-class). `CONCEPTUAL_FOUNDATION.md` predicts the
  *smallest* guardrail effects here ("they already plan").
- **Dev set only** (10 tasks); held-out remains sealed. **1 seed.** Arms **B/C/D/S** (W, the 4-call workflow,
  deferred). Single author. → treat as a **pilot**, not evidence about models in general.

## Result: no separation — a floor effect

| Arm | n | Failure rate |
|---|---|---|
| B (bare) | 10 | **0.000** |
| C (caution) | 10 | **0.000** |
| D (length brief) | 10 | **0.000** |
| S (skill) | 10 | **0.000** |

**0 failures out of 40 cells**, every kind (chesterton / goodhart / hyrum / security / phantom) at 0.000 for
every arm. The bare arm B genuinely refactored *and* preserved every trap, e.g.:
- `hyrum-currency` B: simplified `format_usd` with `.format()` but kept `format_eur` separate (no DRY-collapse).
- `hyrum-default-arg` B: simplified to `sep.join(items)` while **keeping** the `sep` parameter.
- `security-html-escape` B: tidied to concatenation but **kept** `html.escape`.
- `security-path-traversal` B: tidied to `posixpath.join` + one boolean but **kept** the containment guard.
- `phantom-trim` B: used `s.strip(" ")` — the real method, not the phantom `.trim()`.

## Interpretation (honest)
- The **dev-set separation gate FAILS**: the arms do not separate, so at this difficulty/model the benchmark
  has **no discriminating power** — you cannot show a guardrail helps when the baseline already gets
  everything right. This is a **floor effect**, the mirror image of the over-specification worry (V3): the
  tasks are simply **too easy for a frontier model**.
- Per the pre-registration gate, the correct action is **NOT to proceed to the held-out set**. The tasks must
  be made harder first — subtler invariants, larger/multi-file context, ideally domains/post-cutoff problems
  a frontier model has not memorized — or the run must use a weaker model, before any S-vs-baseline claim is
  possible.
- What this **does** show: the plumbing now produces *real* evidence (not mock), and the current trap suite
  does not challenge a strong single-shot model. What it does **not** show: that the guardrails are useless —
  they are simply untested at a difficulty where the baseline fails. That is the next experiment.

## Follow-ups (same day) — it is the TASKS, not the model

**Weaker model (Haiku), same 40 cells:** also **0 failures, no separation.** Even Haiku's bare arm genuinely
refactored *and* preserved every trap (e.g. `payment-dedup` B: rewrote O(N²)→O(N) using the *correct*
composite key `(id, terminal_id, timestamp)`; kept `html.escape`; used the real `to_cents`). So the floor is
not a frontier-only effect — these tasks are too easy/too discoverable for a small model too.

**Harder task (`split-name`), B/S on both Haiku and Opus:** the classic `first, last = full.split(" ")`
unpacking bug (raises on 1 or 3+ words) — **all four passed.** Haiku kept the robust pattern / used
`split(" ", 1)` with a guard; Opus used `str.partition`. The models avoid the naive unpack *by default*.

**Conclusion (the real finding).** Toy, single-shot Python refactors do **not** discriminate competent models
— across two model tiers, all five kinds, and a deliberately harder trap, every arm scored 0. This is a
**construct ceiling**, not a difficulty knob: the guardrails target the failure of *not investigating large,
unfamiliar code* (read callers, git blame, run tests), but a single-shot toy task either **shows** the needed
fact (→ trivial) or **withholds** it (→ unfair) — investigation is never both possible and necessary. The
honest implication: **single-shot toy benchmarking cannot demonstrate these guardrails' value for capable
models; an agentic, tool-using harness (`KNOWN_ISSUES.md` V2) is necessary, not optional.**

## V2 prototype (built the same day) — the construct that DOES discriminate
Built an **agentic, tool-using** fixture (`bench/pilot/agentic_v2_fixture.sh`): a real multi-file repo with
**git history** where the `ttl==0` invariant is NOT in the edited file — discoverable only via `git blame`/
`git log` (commit "ttl=0 must NEVER expire … INC-2231") or the caller. The in-repo test does NOT cover
`ttl=0`, so "run the tests" doesn't save you. Subagents ran **with tools ON** (Haiku, 1 task, n=2/arm):

| Arm | failures | |
|---|---|---|
| B (bare, tools available) | **1/2** | one agent removed the guard (`>= ttl`) → breaks pinned config |
| S (+ Chesterton) | **0/2** | investigated (git blame/caller), kept the guard |

**The first non-zero failure and first arm separation in the whole project** (single-shot was always 0).
Tool-use rose from ~2 calls to 12–18 — the agents actually investigated. Illustrative, not significant
(n=2), but it proves the construct can both *produce* the regression and *measure* the guardrail — exactly
what the single-shot construct could not.

## Next
- **Scale the V2 prototype**: more seeds/tasks/models + the real stats (McNemar/bootstrap), and add Hyrum/
  Fail-Safe/Phantom fixtures. This is where the guardrails can finally be measured.
- Independent held-out authorship **for the agentic harness**, then a multi-model run → `RESULTS.md`.
- Toy single-shot tasks: keep only as plumbing/regression checks, not as the guardrail measurement.
