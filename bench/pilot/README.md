# Subagent pilot — run a real model without an API key

Two ways to put a **real model** behind the benchmark (the `mock` provider is tautological and proves
nothing). **The choice is yours:**

| Provider | How | Pros | Limits |
|---|---|---|---|
| **API** (`--provider anthropic/openai`) | `run_bench.py` + an API key | multi-model, many-seed, reproducible-ish, scales to held-out | needs a key + standard Python; costs $ |
| **Claude Code subagents** (this folder) | dispatch one subagent per (task, arm) | **no key**, runs in-session, real behavior | **one model**, no seed control, slower per call, manual orchestration; pilot-grade only |

## How the subagent pilot works
1. `python bench/pilot/gen.py` — writes the exact per-(task,arm) prompt `run_bench` would send to
   `results/_pilot/prompts/<jid>.txt` and a `jobs.json` index.
2. The orchestrator (Claude Code) dispatches **one subagent per job** as the *model under test*, told to act
   **single-shot and no-tools**: read ONLY its prompt file, write the edited file to
   `results/_pilot/edits[/<variant>]/<jid>.py`. It is forbidden to read any other file (so it cannot peek at
   `hidden_test.py`), run commands, or investigate — faithful to the single-shot construct (`KNOWN_ISSUES` V2).
   Use the Agent `model` override to pick the model (e.g. `haiku`) and a per-model edits subdir.
3. `python bench/pilot/assemble_model.py <edits_subdir> <label>` — collects edits into a run dir; then the
   **unmodified** `bench/judge.py` + `bench/stats.py` score it.

## What the pilots found (2026-06-04) — see `../../PILOT.md`
- Opus-class and Haiku, arms B/C/D/S, all 10–11 dev tasks, 1 seed: **0 failures, no separation (floor).**
- A deliberately harder trap (`split-name`) also passed on both models.
- Conclusion: toy single-shot refactors don't discriminate competent models. The guardrails target failures
  that arise when **investigating large, unfamiliar code with tools** — which this single-shot harness cannot
  represent. The real next step is an **agentic, tool-using harness** (`KNOWN_ISSUES` V2), not harder toy tasks.

Outputs live under `results/` (git-ignored). This folder (`bench/pilot/`) is the tracked, reproducible tooling.

## Agentic (V2) prototype — the construct that DOES discriminate
`agentic_v2_fixture.sh` builds a real multi-file repo **with git history** in `results/_v2/` where the
`ttl==0` invariant is **not stated in the edited file** — only discoverable by `git blame`/`git log` (the
commit "fix(cache): ttl=0 must NEVER expire … INC-2231") or the caller `config_loader.py`. The in-repo test
deliberately does **not** cover `ttl=0`, so "just run the tests" does not save you — you must investigate WHY.

Protocol: copy the template per (arm, seed); dispatch a subagent **with tools ON** (read/grep/git/run-tests)
pointed at its copy; arm B gets the task only, arm S also gets `chestertons-shield/SKILL.md` ("investigate
before changing"). Judge the edited `cache.py` with the held-out `results/_v2/hidden_test.py`.

First prototype (2026-06-04, Haiku, 1 task, n=2/arm — illustrative, not significant):

| Arm | failures | what happened |
|---|---|---|
| B (bare, tools available) | **1/2** | one agent removed the guard (`>= ttl`) → `ttl=0` expires → breaks pinned config |
| S (+ Chesterton) | **0/2** | investigated (git blame/caller) and kept the guard |

This is the **first non-zero failure / first separation** in the project (single-shot was always 0). Tool-use
jumped from ~2 calls (single-shot) to 12–18 (the agents actually investigated). It validates the V2 direction:
unlike toy single-shot, this construct can both *produce* the regression and *measure* the guardrail's effect.
Next: more seeds/tasks/models + stats; this is a prototype, not a result.

