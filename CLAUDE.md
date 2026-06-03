# CLAUDE.md — Open Cognitive Bench (read this first)

Project memory for a fresh Claude Code session. This repo is **local-only** git (no remote yet).

## What this is
Evidence-backed **guardrails for AI coding agents**, shipped as a portable **Skill** *and* an active
multi-agent **Workflow**, and — the point — a **falsifiable, execution-based benchmark** that measures
whether they actually help. Reliability angle (not ideation): **Chesterton's Shield** (investigate why code
exists before changing it) and **Goodhart Attack** (don't game the metric). Benchmarked in spirit against
**Open Collider** (`github.com/CL-ML/open-collider`). See `README.md` + `CONCEPTUAL_FOUNDATION.md`.

## Status (2026-06-02)
- 14+ commits, branch `main`, **local only**, author identity = `Vince427` (repo-local git config).
- **40 trap tasks** (10 dev + 30 held-out). `selfcheck` 40/40. 21 harness unit tests. CI = pure stdlib.
- **5 guardrails / kinds:** chesterton + goodhart (benchmarked-ready); **hyrum + security + phantom = experimental dev-only scaffolds** (2 dev traps each, NOT validated, no held-out — gated behind the dev-set separation check). See `CONCEPTUAL_FOUNDATION.md` → "Candidate guardrails".
- QA M1–M4, L1–L4, N1–N4 resolved/documented; **V1 MITIGATED (de-spoiled + usage.py; V3 open — usage.py may over-specify), V2 DOCUMENTED (scope), PA DONE (power.py)** — see `KNOWN_ISSUES.md`.
- **Power finding:** at 30×5, S-vs-D is well powered but **primary W-vs-S is under-powered for a ~0.10 gap (~40%)** — report it as a CI, not a verdict (`bench/power_analysis.md`).
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
& $py tests/test_harness.py                                                   # 21 harness unit tests
& $py bench/selfcheck.py                                                      # every task is a VALID trap
& $py bench/run_bench.py --tasks bench/tasks/dev --arms B C D S W --seeds 5 --provider mock
& $py bench/judge.py --run results/latest
& $py bench/stats.py --run results/latest
& $py bench/power.py --quick                                                  # design power (LLM-free; ~30s)
```
Real run (needs a standard Python + key): `pip install ".[providers]"`, set `ANTHROPIC_API_KEY`, then
`.\run.ps1 -Provider anthropic -Model claude-sonnet-4-5 -Tasks bench\tasks\dev -Seeds 5` (README → "Run with a real model").

## Map
- `skills/{chestertons-shield,goodhart-attack}/SKILL.md` — the 2 benchmarked guardrails (cross-tool).
- `skills/{hyrums-shield,fail-safe,phantom-check}/SKILL.md` — 3 EXPERIMENTAL guardrails (kinds hyrum/security/phantom; dev-only, not validated).
- `workflows/{antigravity,claude-code}/` — the multi-agent gating workflow (arm W).
- `bench/`: `run_bench.py` (arms B/C/D/S/W, kind-aware, injects `context_files`), `judge.py` (execution metric: chesterton=regression, goodhart=hack), `stats.py` (McNemar+bootstrap+Bonferroni, per-kind, ASCII forest plot), `power.py` (Monte-Carlo power, reuses stats' rule) + `power_analysis.md`, `selfcheck.py`, `providers.py` (anthropic/openai/mock), `extra_mock_answers.py`, `preregistration.md`.
- `bench/tasks/{dev,heldout}/<id>/`: chesterton = `legacy.py`+`hidden_test.py`(+`usage.py` discoverable context); goodhart = stub+`visible_test.py`+`hidden_test.py`. hyrum/security/phantom = correct `legacy.py`+`hidden_test.py` (+context e.g. phantom `helpers.py`), judged as regression like chesterton.
- `tests/test_harness.py`; docs: `CONCEPTUAL_FOUNDATION.md`, `CONTRIBUTING.md`, `KNOWN_ISSUES.md`, `RESULTS.md` (template), `BLOG_POST.md`, `MULTILANG.md`.

## Next work (priority order; see KNOWN_ISSUES.md for detail)
1. ~~V1 de-spoil~~ / ~~V2 scope doc~~ / ~~PA power~~ — **DONE this pass** (de-spoiled 20 `legacy.py` + `usage.py`; scope documented; `power.py`).
2. **Real-model run** → fill `RESULTS.md` (needs standard Python + API key). Given the PA finding, treat W-vs-S as a CI, not a verdict, at 30×5.
3. Optional: **agentic tool-using harness** (true V2 fix — git history/callers/run-tests as real tools; needs an LLM).
4. Optional: N3 multilang runner (`dotnet`/`node`, see `MULTILANG.md`), `src/` packaging, publish under `Vince427`.
5. Promote the 3 EXPERIMENTAL guardrails (hyrum/security/phantom) — now scaffolded (skill + 2 dev traps each, `selfcheck`-valid) but NOT validated: each needs held-out tasks + a real-model result, and the 2 existing must pass the dev-set separation gate first. `Fail-Safe` is the highest-value. See `CONCEPTUAL_FOUNDATION.md` → "Candidate guardrails".

## Conventions
Pure stdlib (no deps for mock/selfcheck/tests); LF; every skill must ship with a benchmark result (including a
negative one); publish `RESULTS.md` regardless of outcome; the parallel-lens pattern is not novel — the
contribution is the *specific guardrails + the evidence*.
