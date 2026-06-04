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

## Next
Harder tasks (or a weaker/older model), then re-run this same pilot; only once arms separate on dev does the
held-out run become meaningful. Optionally add arm W and more seeds.
