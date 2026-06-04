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
