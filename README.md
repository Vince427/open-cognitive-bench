# Open Cognitive Bench

> **Does a multi-agent *cognitive-gating workflow* actually beat a strong single-agent + skill at
> stopping an AI from breaking your code — and is it worth the 5–10× cost?**
> Nobody has measured it. This repo ships both artifacts *and* the falsifiable benchmark that decides —
> **negative results included.**

Most damage an AI coding agent does to a codebase isn't a *knowledge* failure — it's a **respect**
failure (silently destroying a hidden invariant) and a **metric-gaming** failure (satisfying the test,
betraying the intent). The fashionable answer is "drop a clever Markdown rules file." The honest answer
is: *prove it moved a number on held-out tasks.*

Open Cognitive Bench packages the two best-evidenced guardrails — **Chesterton's Shield** (investigate
*why* code exists before changing it) and **Goodhart Attack** (anticipate how a change games the metric)
— in **two forms**, and benchmarks them against each other:

| | What it is | Portable? |
|---|---|---|
| **Skill** (`skills/*/SKILL.md`) | A passive `.md` rule injected into a single agent. Cross-tool open standard. | ✅ Claude Code / Antigravity / Cursor / Codex |
| **Workflow** (`workflows/`) | An *active* multi-agent panel: lens sub-agents investigate in parallel and **gate** the implementer. | ❌ Antigravity + Claude Code only (orchestration isn't portable yet) |

## The open question this benchmark answers

Recent work shows a well-engineered **single agent can match or beat** many multi-agent workflows
(arXiv:2601.12307), while multi-agent setups add 5–10× cost and real coordination-failure modes
(arXiv:2601.04748). **No one has tested this for code guardrails.** We do — with a pre-registered,
execution-based, paired benchmark.

### Arms

| Arm | Mode | Purpose |
|---|---|---|
| **B** | Solo agent, bare: "refactor/optimize this" | floor |
| **C** | Solo + "be careful, don't break anything" | isolates *skill* vs *mere instruction* |
| **D** | Solo + a length/context-matched brief (no investigate-before-changing rule) | isolates *the rule* vs *mere prompt length* |
| **S** | Solo + **Skill** (`chestertons-shield`) | the **strong baseline** (hard to beat) |
| **W** | **Workflow** multi-agent gating panel | the active mode under test |

The **D** arm is the falsifier that the incumbents (and even Open Collider's critics) demand: because the
`S` system prompt is longer than `B`, a naive `S > B` win could just be "more tokens." `D` is a verbose,
ruleless brief of comparable length — **if `S` beats `D`, the effect is the rule, not the length.** The
report prints per-arm input tokens so the S/D length parity is verifiable.

**Primary, pre-registered question:** *does W beat S on the held-out failure rate, and by how much net
of cost?* The metric is **execution-based**, paired across arms, multi-seed, with McNemar + bootstrap CIs
and Bonferroni correction. See `bench/`.

**Two guardrail dimensions, two failure modes** (each falsified by execution, reported separately by `stats.py`):
- **Chesterton tasks** — the agent gets correct-but-ugly code to refactor; *failure = regression* (its edit
  breaks a hidden invariant). Arm `S` injects `chestertons-shield`.
- **Goodhart tasks** — the agent gets a stub + a deliberately weak *visible* test to make pass; *failure =
  "hack"* (the visible test passes but a held-out *hidden* behavior test fails — it gamed the metric). Arm
  `S` injects `goodhart-attack`.

## Scope
The benchmark currently targets **Python** tasks (the harness executes Python hidden tests). The design is
language-agnostic, but a multi-language runner (C#/JS via `dotnet`/`node`) is **future work** (see
`KNOWN_ISSUES.md` N3). The skills and workflows themselves are language-agnostic.

## Honesty policy

- The "parallel lenses + critic that gates" pattern is **not novel** (Claude Code Ultra Plan, DeepMind
  Co-Scientist, the multi-agent-debate literature). Our contribution is the **specific lenses + the evidence**,
  not the orchestrator.
- We publish runs **even when W does not beat S**, or when the cost isn't worth it. That's the point.

## Quick start

No third-party packages are required for the mock run (pure Python 3.9+ stdlib). `pip install -r
requirements.txt` only adds the optional model SDKs (for real runs) and `pytest`.

```bash
# 0) Sanity: every task is a valid trap (original passes, naive rewrite breaks the invariant)
python bench/selfcheck.py
# 1) Smoke-test the whole harness with NO API key and NO spend (deterministic mock provider):
python bench/run_bench.py --tasks bench/tasks/dev --arms B C D S W --seeds 5 --provider mock
python bench/judge.py     --run results/latest
python bench/stats.py     --run results/latest
```

### Run with a real model (when you have a standard Python install)

`python`/`py` is not bundled with Windows — install Python 3.11+ from python.org (tick "Add to PATH"),
then:

```powershell
pip install anthropic openai          # only needed for real runs; pytest is optional
setx ANTHROPIC_API_KEY "sk-ant-..."   # or OPENAI_API_KEY; reopen the terminal afterwards
# Iterate on the DEV set first:
.\run.ps1 -Provider anthropic -Model claude-sonnet-4-5 -Tasks bench\tasks\dev -Seeds 5
# Linux/macOS: ./run.sh anthropic claude-sonnet-4-5 bench/tasks/dev 5
```

`run.ps1` / `run.sh` just chain `run_bench → judge → stats`. **Before** touching the held-out set, freeze
`bench/preregistration.md` (commit it), then run **once** with `-Tasks bench\tasks\heldout`.

Then set `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` and swap `--provider anthropic` (or `openai`).
**Iterate only on `bench/tasks/dev/`.** Keep `bench/tasks/heldout/` sealed; score it **once** at the end,
after freezing `bench/preregistration.md`.

## Install as a skill (cross-tool)

```
/plugin marketplace add Vince427/open-cognitive-bench
/plugin install chestertons-shield@open-cognitive-bench
```

## Status

PoC scaffold with **34 validated trap tasks** (4 dev + 30 held-out, across both guardrail dimensions; all
pass `bench/selfcheck.py`). The harness runs end-to-end in `--provider mock`. The only remaining step is the
**real-model run** (set an API key and use `run.ps1` / `run.sh`); for a publishable result, ideally have an
independent contributor expand or replace the held-out tasks.

## Docs
- [`CONCEPTUAL_FOUNDATION.md`](CONCEPTUAL_FOUNDATION.md) — why these guardrails should work (evidence-grounded).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to author trap tasks (and the held-out independence rule).
- [`bench/preregistration.md`](bench/preregistration.md) — freeze before the held-out run.
- [`RESULTS.md`](RESULTS.md) — results template (fill after the real run).
- [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md) — QA findings & their status.
- [`BLOG_POST.md`](BLOG_POST.md) — the rationale post (why benchmark guardrails at all).
- [`MULTILANG.md`](MULTILANG.md) — design for multi-language tasks (C#/JS) + the canonical C# trap.

Install (optional): `pip install ".[providers]"` for real-model runs, `".[dev]"` for lint/test. Mock runs need nothing.

## License

MIT (code) — see `LICENSE`. Benchmark data CC BY 4.0.
