# CLAUDE.md — Open Cognitive Bench (read this first)

Project memory for a fresh Claude Code session. This repo is **local-only** git (no remote yet).

## What this is
Evidence-backed **guardrails for AI coding agents**, shipped as a portable **Skill** *and* an active
multi-agent **Workflow**, and — the point — a **falsifiable, execution-based benchmark** that measures
whether they actually help. Reliability angle (not ideation): **Chesterton's Shield** (investigate why code
exists before changing it) and **Goodhart Attack** (don't game the metric). Benchmarked in spirit against
**Open Collider** (`github.com/CL-ML/open-collider`). See `README.md` + `CONCEPTUAL_FOUNDATION.md`.

## Status (2026-06-02)
- 13+ commits, branch `main`, **local only**, author identity = `Vince427` (repo-local git config).
- **34 trap tasks** (4 dev + 30 held-out = 18 chesterton + 12 goodhart). `selfcheck` 34/34. 16 harness unit tests. CI = pure stdlib.
- QA M1–M4, L1–L4, N1–N4 resolved/documented; **V1/V2 validity findings OPEN** — see `KNOWN_ISSUES.md`.
- **No real-model results yet.** `--provider mock` is a deterministic simulator (tautological). The empirical run is the missing piece.

## CRITICAL gotchas
- **No standard Python on this machine** (`python`/`py` are Windows-Store stubs). Use the embedded CPython 3.12:
  `& "C:\Program Files\LibreOffice\program\python.exe"`. The harness is pure stdlib, so it runs there.
- **Mock ≠ evidence.** Never report mock numbers as results.
- **Held-out is sealed:** don't tune skills against `bench/tasks/heldout/`; freeze `bench/preregistration.md`, then score it once.
- Git local only; LF enforced (`.gitattributes`); commit messages end with the Co-Authored-By trailer.

## Run it
```
$py = "C:\Program Files\LibreOffice\program\python.exe"
& $py tests/test_harness.py                                                   # 16 harness unit tests
& $py bench/selfcheck.py                                                      # every task is a VALID trap
& $py bench/run_bench.py --tasks bench/tasks/dev --arms B C D S W --seeds 5 --provider mock
& $py bench/judge.py --run results/latest
& $py bench/stats.py --run results/latest
```
Real run (needs a standard Python + key): `pip install ".[providers]"`, set `ANTHROPIC_API_KEY`, then
`.\run.ps1 -Provider anthropic -Model claude-sonnet-4-5 -Tasks bench\tasks\dev -Seeds 5` (README → "Run with a real model").

## Map
- `skills/{chestertons-shield,goodhart-attack}/SKILL.md` — the guardrails (cross-tool).
- `workflows/{antigravity,claude-code}/` — the multi-agent gating workflow (arm W).
- `bench/`: `run_bench.py` (arms B/C/D/S/W, kind-aware), `judge.py` (execution metric: chesterton=regression, goodhart=hack), `stats.py` (McNemar+bootstrap+Bonferroni, per-kind), `selfcheck.py`, `providers.py` (anthropic/openai/mock), `extra_mock_answers.py`, `preregistration.md`.
- `bench/tasks/{dev,heldout}/<id>/`: chesterton = `legacy.py`+`hidden_test.py`; goodhart = stub+`visible_test.py`+`hidden_test.py`.
- `tests/test_harness.py`; docs: `CONCEPTUAL_FOUNDATION.md`, `CONTRIBUTING.md`, `KNOWN_ISSUES.md`, `RESULTS.md` (template), `BLOG_POST.md`, `MULTILANG.md`.

## Next work (priority order; see KNOWN_ISSUES.md for detail)
1. **V1 — de-spoil traps (LLM-free).** Remove the 14 invariant-giveaway comments in `legacy.py`; make the invariant *discoverable* (sibling callers/usage file or an existing passing test in the prompt), not stated.
2. **V2 — document the single-shot/no-tools scope** (or design an agentic tool-using harness — needs an LLM).
3. **PA — power analysis** (Monte-Carlo McNemar, LLM-free).
4. **Real-model run** → fill `RESULTS.md` (needs standard Python + API key).
5. Optional: N3 multilang runner (`dotnet`/`node`, see `MULTILANG.md`), `src/` packaging, publish under `Vince427`.

## Conventions
Pure stdlib (no deps for mock/selfcheck/tests); LF; every skill must ship with a benchmark result (including a
negative one); publish `RESULTS.md` regardless of outcome; the parallel-lens pattern is not novel — the
contribution is the *specific guardrails + the evidence*.
