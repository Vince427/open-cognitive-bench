# CLAUDE.md — Open Cognitive Bench (read this first)

Project memory for a fresh Claude Code session. Pushed to a **PUBLIC** GitHub remote
`github.com/Vince427/open-cognitive-bench` (origin/main, synced; made public 2026-06-05). `gh` is installed at
`C:\Program Files\GitHub CLI\gh.exe` and authed as `Vince427` (token scopes: repo, workflow).

## What this is
Evidence-backed **guardrails for AI coding agents**, shipped as a portable **Skill** *and* an active
multi-agent **Workflow**, and — the point — a **falsifiable, execution-based benchmark** that measures
whether they actually help. Reliability angle (not ideation): **Chesterton's Shield** (investigate why code
exists before changing it) and **Goodhart Attack** (don't game the metric). Benchmarked in spirit against
**Open Collider** (`github.com/CL-ML/open-collider`). See `README.md` + `CONCEPTUAL_FOUNDATION.md`.
**Pivot (honest):** the guardrail-benchmark thesis came out mostly negative; the repo now leads with
`drift-guard/` (a working tool against iterative-rewrite drift) + the methodology/negative-results. See Status.

## Status (2026-06-04) — full picture in `REPORT.md` / `PAPER.md`
- `main`, pushed to **public** GitHub (synced). **selfcheck 41/41, harness 21/21, drift-guard 11/11 unit + 4 fuzz suites (800+ random cases) + multipass demo + integrations 12/12.** CI = pure stdlib + drift-guard tests.
- **The honest result (the guardrail thesis did NOT pan out — `PAPER.md`):** a **single-shot** benchmark **can't** measure these guardrails on capable models (Opus & Haiku, every arm **0/40** — V5 *construct ceiling*). An **agentic, tool-using** harness (`bench/agentic/`, rounds 1–4) CAN produce failures, but the measured "skill" effect is **instruction-resistance (sycophancy), NOT investigation**: with a *neutral* instruction the gap **vanishes** (round 4: B 0/12 = S 0/12).
- **FLAGSHIP DELIVERABLE = `drift-guard/`** (the project's clearest positive). Stops iterative-rewrite drift ("broken telephone"): an executable **fact-gate GUARANTEES** the facts you list survive every rewrite; the **skill only REDUCES** (a prompt can't guarantee — Data-Processing-Inequality, see `DRIFT.md`). Works on code + prose; ships `gate.py`, `guarded_rewrite.py` (auto loop), `SKILL.md`, `extract_facts_prompt.md`, `test_gate.py` (11 unit tests, incl. anti-fact), `test_gate_fuzz.py` (4 property suites / 800+ random cases — the guarantee, fuzzed), `example/multipass_demo.py` (offline many-passes gated-vs-ungated demo), `integrations/` (CI/hook/loop/MCP, 12 tests) — all in CI.
- 41 trap tasks (11 dev + 30 held-out). 5 guardrails: chesterton+goodhart (benchmarked-ready), **hyrum/security/phantom = EXPERIMENTAL, unvalidated**. QA findings **V1–V5** + power + calibration in `KNOWN_ISSUES.md`.
- **Public-readiness: GREEN.** No secrets/PII (only a placeholder `sk-ant-...` in README). **Citations verified 2026-06-04** — only **7 arXiv IDs** repo-wide, all confirmed (1606.06565, 2305.17493, 2306.05685, 2310.13548, 2410.21012, 2502.20258, 2603.08520) + Nature 2024; unverified ones removed. Honest (negative results, single-author, Open Collider credited). **Made public 2026-06-05.**

## Resume / session state (to continue WITHOUT loss)
- **Remote & branches:** `gh` installed + authed (Vince427, repo+workflow). Go public when ready:
  `& "C:\Program Files\GitHub CLI\gh.exe" repo edit Vince427/open-cognitive-bench --visibility public`.
  Branches `agentic-harness` + `drift-guard-v2` are **merged into main** (delete to tidy: `git push origin --delete <b>` + `git branch -d <b>`).
- **Out-of-tree run artifacts (git-ignored, REGENERABLE, likely GONE next session):** `~/ocb_agentic`, `~/ocb_agentic_neutral` (agentic fixtures — rebuild: `bash bench/agentic/build.sh`, fixtures go to `$HOME/ocb_agentic` per `$OCB_AGENTIC`), `~/ocb_drift`, `~/ocb_extract` (drift demo). The pilots used **Claude Code subagents as the model under test** (no API key) — protocol in `bench/pilot/README.md` + `bench/agentic/README.md`.
- **Open decisions (yours):** (1) make the repo public; (2) delete merged branches; (3) get an **INDEPENDENT author** for held-out/agentic fixtures + an **independent review of the DPI math** (the load-bearing credibility fix); (4) a **powered multi-model run** (needs API budget) — **expect the "skill helps investigation" claim to stay null**.
- **Proven vs not (don't overclaim):** drift-guard **gate = real guarantee** (trivial logic, on the facts you list); **skill = reduces, empirical/unproven**; **drift-without-checks = standard theorem (DPI)**. The benchmark's W-vs-S question is **empirically unanswered at scale**.

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
& $py drift-guard/test_gate.py                                                # 11 drift-guard unit tests (incl. anti-fact)
& $py drift-guard/test_gate_fuzz.py                                           # 4 property suites, 800+ random cases (the guarantee, fuzzed)
& $py drift-guard/example/multipass_demo.py                                   # offline gated-vs-ungated multi-pass drift demo
& $py drift-guard/gate.py --facts drift-guard/example/policy.facts.txt --file drift-guard/example/policy.md
```
Real run (needs a standard Python + key): `pip install ".[providers]"`, set `ANTHROPIC_API_KEY`, then
`.\run.ps1 -Provider anthropic -Model claude-sonnet-4-5 -Tasks bench\tasks\dev -Seeds 5` (README → "Run with a real model").

## Map
- **`drift-guard/`** — FLAGSHIP standalone tool: `gate.py` (executable fact-gate, code+prose), `guarded_rewrite.py` (auto edit→gate→accept/revert loop), `SKILL.md` (Drift Shield), `extract_facts_prompt.md`, `test_gate.py` (11 tests) + `test_gate_fuzz.py` (4 property suites/800+ cases) + `example/multipass_demo.py` (offline drift demo) + `integrations/` (CI/hook/loop/MCP, 12 tests), all in CI; `example/`. See its `README.md`.
- **`bench/agentic/`** — the V2 tool-using harness (real repo + git history; rounds 1–4 + the drift demo): `build.sh` (out-of-tree fixtures), `score.py`, `drift_seed.py`/`drift_check.py`/`drift_shield.md`, `README.md`.
- **`bench/pilot/`** — run a real model with NO API key (Claude Code subagents): `gen.py`, `assemble_model.py`, `README.md`.
- top-level docs: **`PAPER.md`** (arXiv-style, the math + the honest arc), **`DRIFT.md`** (drift literature + DPI/decay math), **`REPORT.md`** (global status), **`PILOT.md`** (real-model pilots).
- `skills/{chestertons-shield,goodhart-attack}/SKILL.md` — the 2 benchmarked guardrails (cross-tool).
- `skills/{hyrums-shield,fail-safe,phantom-check}/SKILL.md` — 3 EXPERIMENTAL guardrails (kinds hyrum/security/phantom; dev-only, not validated).
- `workflows/{antigravity,claude-code}/` — the multi-agent gating workflow (arm W).
- `bench/`: `run_bench.py` (arms B/C/D/S/W, kind-aware, injects `context_files`), `judge.py` (execution metric: chesterton=regression, goodhart=hack), `stats.py` (McNemar+bootstrap+Bonferroni, per-kind, ASCII forest plot), `power.py` (Monte-Carlo power, reuses stats' rule) + `power_analysis.md`, `selfcheck.py`, `providers.py` (anthropic/openai/mock), `extra_mock_answers.py`, `preregistration.md`.
- `bench/tasks/{dev,heldout}/<id>/`: chesterton = `legacy.py`+`hidden_test.py`(+`usage.py` discoverable context); goodhart = stub+`visible_test.py`+`hidden_test.py`. hyrum/security/phantom = correct `legacy.py`+`hidden_test.py` (+context e.g. phantom `helpers.py`), judged as regression like chesterton.
- `tests/test_harness.py`; docs: `CONCEPTUAL_FOUNDATION.md`, `CONTRIBUTING.md`, `KNOWN_ISSUES.md`, `RESULTS.md` (template), `BLOG_POST.md`, `MULTILANG.md`.

## Next work (priority; detail in REPORT.md / KNOWN_ISSUES.md)
DONE this arc: V1/V2/PA, the agentic harness (rounds 1–4), the iterative-drift demo, **drift-guard v2**
(gate + loop + extraction + CI tests), reframed README around drift-guard, **citations verified**, pushed to
**public** GitHub, added `QUICKSTART.md`. All offline high-value work is complete.
1. **Decide & act (yours):** repo is **public** (done 2026-06-05); optionally delete the merged branches.
2. **Independent validation** (the credibility blocker — needs a 3rd party): independent author for held-out /
   agentic fixtures; independent review of the **DPI math** in `DRIFT.md`.
3. **Powered run** (needs API budget): ≥2 models × dozens of seeds/fixtures on the agentic harness → `RESULTS.md`.
   Expect the "skill helps *investigation*" claim to stay null; the publishable wins are **drift-guard + the methodology**.
4. **Harden drift-guard for real use:** a fact-extraction helper that auto-drafts the fact-set (LLM proposes,
   human approves once) is the key UX gap; a real `--rewrite-cmd` wired to a model.
5. Optional/low-value: promote the 3 EXPERIMENTAL guardrails (only after a discriminating run); N3 multilang; `src/` packaging.

## Conventions
Pure stdlib (no deps for mock/selfcheck/tests); LF; every skill must ship with a benchmark result (including a
negative one); publish `RESULTS.md` regardless of outcome; the parallel-lens pattern is not novel — the
contribution is the *specific guardrails + the evidence*.
