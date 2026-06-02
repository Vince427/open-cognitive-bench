# Known Issues — QA findings

Status date: 2026-06-01. Scope: static review + targeted probes of the benchmark harness
(`bench/run_bench.py`, `judge.py`, `stats.py`, `providers.py`, `selfcheck.py`), the tasks, and the docs.

**Overall:** the harness is sound and honest **for the mock provider** (`selfcheck` 34/34; paired McNemar +
bootstrap + Bonferroni correct; sealed held-out). The items below are **real-run-only** problems the mock
smoke test cannot surface (the mock always emits clean, ` ```python `-fenced output, so it hides M2, and it
never calls a real API, so it hides M1/L1/L2). None block the mock pipeline. M1–M4 should be fixed **before**
drawing conclusions from a real-model run.

---

## Resolution log — 2026-06-02 (all addressed)
- **M1 — FIXED.** `--temperature` (default 0.7) added to `run_bench.py`, threaded into both providers, recorded in `meta.json`.
- **M2 — FIXED.** `CODE_RE` accepts any language tag (` ```py `, ` ```python3 `, bare ` ``` `) and requires a newline before the body. Verified by probe.
- **M3 — FIXED.** `stats.py` prints a *Goodhart detail* table (hacked / correct / incompetent + hack rate + conditional hack), so incompetence cannot masquerade as low failure.
- **M4 — RESOLVED (documented).** `run_workflow` and both `workflows/*.md` now state arm W is a single-pass panel; the BLOCK/re-investigate loop stays a design target.
- **L1 — DOCUMENTED.** Anthropic has no `seed`; noted in `providers.py` (runs non-reproducible by design; temperature is recorded).
- **L2 — HARDENED + DOCUMENTED.** OpenAI `seed`/`temperature` now passed conditionally; reasoning-model limitation noted.
- **L3 — FIXED.** Unused `entrypoint` removed from all `task.json`.
- **L4 — FIXED.** Default Anthropic model updated to `claude-sonnet-4-5`.

The detailed findings below are kept as the historical record; the "by design" and "verified sound" sections still apply.

---

## Second review — 2026-06-02
- **bench/README arm count — FIXED.** Said "four arms (B/C/S/W)"; now "five arms (B/C/D/S/W)".
- **N1 (LLM judge doc≠code) — FIXED (doc).** `bench/README.md` now states the metric is execution-only plus
  an advisory `artifact_ok` regex; a full LLM-as-judge is marked explicit future work (not implemented).
- **N2 — FIXED.** `tests/test_harness.py` unit-tests the harness (McNemar exact, bootstrap, percentile/mean,
  `extract_code` incl. the M2 fix, and the judge execution runner) — 16 tests, dual-mode (pytest or
  `python tests/test_harness.py`), run by CI.
- **N3 — DOCUMENTED.** Scope stated as Python-first in `README.md` (## Scope). A multi-language runner
  (C#/JS via `dotnet`/`node`) + non-Python traps remain future work (needs those runtimes to validate).
  Runner design + the canonical C# trap are written up in `MULTILANG.md`.
- **N4 — FIXED.** Placeholders set to `Vince427` in `README.md` and `.claude-plugin/marketplace.json`.
- **Added this pass:** `CONCEPTUAL_FOUNDATION.md`, `CONTRIBUTING.md`, `RESULTS.md` (template), `.env.example`.
- **Polish (later pass):** `tests/test_harness.py`, `pyproject.toml` (metadata + extras + ruff/pytest config),
  `BLOG_POST.md` (rationale post), `MULTILANG.md` (multi-language design + C# trap).

---

## 🟠 Medium

### M1 — Temperature is never applied
- **Where:** `bench/providers.py` (`AnthropicProvider.complete`, `OpenAIProvider.complete`), `bench/run_bench.py`.
- **Evidence:** `grep -i temperature` matches only `preregistration.md` (which fixes **T = 0.7**) and an
  unrelated invariant string. Neither provider passes a `temperature` argument, so the API default (~1.0) is used.
- **Impact:** runs do not match the pre-registered T = 0.7; decoding is not controlled/recorded as claimed.
- **Suggested fix:** add `--temperature` to `run_bench.py`, thread it into both providers, and record it in
  `results/<run>/meta.json`.

### M2 — Code extraction corrupts non-`python` fenced blocks
- **Where:** `bench/run_bench.py` → `extract_code`, regex `` r"```(?:python)?\s*(.*?)```" ``.
- **Evidence (probe run):**
  - `` ```py\nprint(1)\n``` `` → `'py\nprint(1)\n'` (the `py` language tag leaks into the code)
  - `` ```python3\nx=2\n``` `` → `'3\nx=2\n'`
  - `` ```python … ``` `` and bare `` ``` … ``` `` → correct.
- **Impact:** a real model that fences with `` ```py ``, `` ```python3 ``, etc. yields a file with a **syntax
  error** → spurious failure (false regression / false "incompetent"). Models vary in their fence label.
- **Suggested fix:** accept any language tag, e.g. `` r"```[a-zA-Z0-9_+-]*\n(.*?)```" `` (and/or strip a
  leading bare language line from the captured block).

### M3 — Goodhart failure metric ignores "incompetent" output
- **Where:** `bench/judge.py` (goodhart branch: `failed = hacked`, where `hacked = visible_pass and not hidden_pass`).
- **Impact:** a run that does not even pass the **visible** test is labeled `incompetent` and scored
  `failed = False`. So an arm that emits invalid/garbage code shows an artificially **low** failure rate
  (looks great). It is also **asymmetric** with chesterton, where invalid code *does* count as failure.
  `stats.py` aggregates only `failed` and does not surface the hacked / correct / incompetent split (the
  `detail` field is in `judgments.jsonl` but not reported).
- **Suggested fix:** report all three rates per arm in `stats.py`, and/or define the goodhart hack rate
  **conditional on passing the visible test** (and report the visible-pass rate alongside it).

### M4 — Workflow harness is a linear pass, not the gating loop in the docs
- **Where:** `bench/run_bench.py` → `run_workflow` (lens → lens → synth → implementer, single pass) vs.
  `workflows/antigravity/gated-change.md` and `workflows/claude-code/orchestrator.md` (which describe a
  `// if BLOCK → re-investigate` gate before the implementer runs).
- **Impact:** doc-vs-implementation gap; the harness under-delivers what the workflow docs promise, so a
  "W" result does not reflect the full gating design.
- **Suggested fix:** either implement the BLOCK/re-investigate loop in `run_workflow`, or state explicitly in
  the workflow docs that the benchmarked W is a single-pass (best-effort) panel.

---

## 🟡 Low

### L1 — Anthropic provider ignores `seed`
- `AnthropicProvider` passes no `seed` (the Messages API has none). Multi-seed runs are therefore independent
  samples at the default temperature (variance is fine) but **not reproducible**. Tie the fix to M1
  (record decoding params; accept that Anthropic runs are non-deterministic).

### L2 — OpenAI provider may break on reasoning models
- `OpenAIProvider` hard-codes `max_tokens` and `seed`. Reasoning models (o-series / gpt-5-class) require
  `max_completion_tokens` and reject `temperature`/`seed`. `gpt-4o` works. Document supported models or
  branch per model family.

### L3 — `entrypoint` field is inconsistent and unused
- 8 of 34 `task.json` files carry an `entrypoint` key; the other 26 (and all goodhart tasks) do not. The
  harness never reads it. Either populate it everywhere or drop it.

### L4 — Stale default Anthropic model
- `AnthropicProvider` defaults to `claude-3-5-sonnet-latest`, likely outdated by 2026. Minor: callers pass
  `--model`. Update the default.

---

## ℹ️ By design / already documented (not bugs)
- The **mock provider is tautological** — break probabilities are hard-coded; it validates plumbing/stats only,
  not real-model behavior (see `bench/README.md`).
- The **held-out set was authored by the skill author** — for a publishable result, have an independent
  contributor add/replace tasks (see `bench/tasks/heldout/README.md`, `bench/preregistration.md`).
- **Workflows are not portable** across tools (only Skills are) — `W` targets Antigravity + Claude Code only.

---

## ✅ Verified sound
- Arm naming **B/C/D/S/W** consistent across code, docs, CI (`grep "B C S W"` → 0 hits).
- `bench/selfcheck.py`: **34/34** tasks valid (chesterton original passes / naive rewrite fails; goodhart
  correct passes both / hacked games the visible test).
- Stats: paired design, McNemar exact (two-sided binomial on discordant pairs), bootstrap CIs (task-clustered),
  Bonferroni across the 5 comparisons — all correct.
- Chesterton execution metric is robust; tasks use integer-exact cases (no float-equality flakiness).
- Held-out runs are git-ignored (`results/run-*/`); only `results/.gitkeep` is tracked. CI is pure stdlib.
