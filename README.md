# Open Cognitive Bench

**What this repo is, honestly (2026-06-04).** It set out to be a falsifiable benchmark for "guardrail" prompts
that supposedly stop an AI coding agent from breaking your code. The rigorous finding is **mostly negative**,
and that reshaped the project. It is now two things:

1. **[`drift-guard/`](drift-guard/README.md) — a small tool that actually works** (the clearest positive
   here). It stops an LLM from silently dropping facts when it re-edits a document over many passes
   ("broken-telephone" drift). An **executable fact-gate _guarantees_** the facts you list survive every
   rewrite; a **skill ("Drift Shield") only _reduces_** the loss. The guarantee is the *gate*, not the prompt
   — and the math says why ([`DRIFT.md`](DRIFT.md)). **Start here if you want something usable.**
2. **A falsifiable benchmark + an honest methodology** for guardrail claims — including the controls that
   repeatedly killed our *own* positive results. Useful as "how to (not) benchmark coding-agent guardrails,"
   **not** as proof that guardrails make agents safer.

> **One-paragraph result.** Real-model pilots show a **single-shot** benchmark **can't** measure these
> guardrails on capable models (every arm scores 0 — a *construct ceiling*). An agentic, tool-using harness
> *can* produce failures, but the measured "skill effect" is mostly **resisting a misleading instruction**
> (sycophancy), **not investigation**: with a *neutral* instruction the gap vanishes. Details:
> [`PAPER.md`](PAPER.md) (arXiv-style, with math), [`REPORT.md`](REPORT.md), [`PILOT.md`](PILOT.md).

The two guardrails we tried to validate — **Chesterton's Shield** (investigate *why* code exists before
changing it) and **Goodhart Attack** (anticipate how a change games the metric) — ship as a portable Skill
(`skills/*/SKILL.md`, cross-tool) and an active multi-agent Workflow (`workflows/`, Claude Code/Antigravity).
The benchmark below is how we (tried to) test them.

**Inspired by [Open Collider](https://github.com/CL-ML/open-collider).** We borrow its ethos — ship the
artifact *and* a falsifiable benchmark, publish negative results — and its presentation (forest plot +
falsifier-control arms), but apply it to **reliability** (judged by **execution**: a test passes or fails)
instead of **ideation** (judged by **LLM preference**). Open Collider reports a strong *positive* in its
domain; we report a mostly-negative methodological result in ours. Honest head-to-head in [`PAPER.md` §7](PAPER.md).

## How the pieces run: gate (guarantee) vs skill (nudge)
Two **opposite** mechanisms — don't confuse them:
- **A skill** (`*/SKILL.md`) is a **prompt** injected into an LLM agent. It *shapes* behavior ("preserve the
  load-bearing facts"). No code runs → it **reduces** mistakes but **cannot guarantee** anything.
- **A gate / CI** is **code that runs and rejects** a bad result. `drift-guard/gate.py` checks that the facts
  you listed survive a rewrite (revert if not); the repo's **CI** (`.github/workflows/ci.yml`) runs the tests
  + `selfcheck` on every push and goes red on any regression. **This is the part that guarantees.**
- They compose: the skill lowers how often the gate must reject; the gate (and CI) provide the guarantee.
  *A CI for code is a fact-gate for a document — the same idea at two levels.*

## The benchmark — what we set out to test (and what we found)

We set out to ask: does a guardrail **Skill** (and a multi-agent **Workflow**) actually lower the rate at
which an agent breaks code, net of cost — a question nobody had tested for code guardrails, with a
pre-registered, execution-based, paired design. **What we found instead:** the single-shot version can't
discriminate, and the agentic version's apparent effect is instruction-resistance, not investigation (see the
one-paragraph result above and [`PAPER.md`](PAPER.md)). The design below stands as a *methodology*; treat its
arms as the apparatus, not as a delivered positive result.

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

**Pre-registered primary question (what the apparatus targets):** *does W beat S on the held-out failure
rate, net of cost?* — execution-based, paired across arms, multi-seed, with McNemar + bootstrap CIs and
Bonferroni. **It is empirically unanswered at scale** (the single-shot pilots floored; see the result above).
See `bench/`.

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

### What is actually measured (construct & its limits)
This benchmark measures a **single-shot, no-tools** effect: each arm is given the file (plus, for chesterton
tasks, a read-only `usage.py` showing how the code is called) in **one prompt** and returns **one** edited
file. There is no git history to `blame`, no filesystem to grep, and the model cannot run commands. So the
Chesterton skill's literal "run `git blame`, find the callers, read the tests" steps are exercised **only
over what is in the prompt** — the agent must *attend to the provided `usage.py`* rather than truly
investigate a repo. The result therefore speaks to a **prompt/skill effect under one-shot conditions**, not
to a tool-using investigative loop. Measuring the latter needs an agentic, tool-calling harness (and a live
model); that is deliberately out of scope here (`KNOWN_ISSUES.md` V2).

The invariant is **discoverable, not stated**: chesterton `legacy.py` files do **not** spell out the
invariant in a comment (that would reduce the task to "did the model read the comment"). Instead the special
case is visible in the *structure* and the *reason* is discoverable from the injected `usage.py` caller — so
the skill's marginal value is "does it make the agent investigate before simplifying," not "did everyone see
the same giveaway" (`KNOWN_ISSUES.md` V1). `payment-dedup` is the reference design (invariant implied by
structure alone).

### Is the design adequately powered?
`python bench/power.py` is a pure-stdlib Monte-Carlo power analysis (no LLM) that reuses the **exact**
McNemar + bootstrap decision rule the report uses. Headline finding at the proposed **30 tasks × 5 seeds**:
the rule-isolation comparison **S vs D** is fully powered, but the **primary W vs S** comparison is
**under-powered for a small (≈0.10) absolute gap** (~40% power) — so a null W-vs-S result there should be
read as "underpowered," and detecting it would need more tasks/seeds. See `bench/power_analysis.md`.

## Honesty policy

- The "parallel lenses + critic that gates" pattern is **not novel** (Claude Code Ultra Plan, DeepMind
  Co-Scientist, the multi-agent-debate literature). Our contribution is the **specific lenses + the evidence**,
  not the orchestrator.
- We publish runs **even when W does not beat S**, or when the cost isn't worth it. That's the point.

## Quick start

**drift-guard (the usable tool) — pure stdlib, no key:**
```bash
python drift-guard/gate.py --facts drift-guard/example/policy.facts.txt --file drift-guard/example/policy.md
python drift-guard/gate.py --facts drift-guard/example/policy.facts.txt --file drift-guard/example/policy_drifted.md  # exit 1: facts lost
python drift-guard/test_gate.py        # 10 tests
```
See [`drift-guard/README.md`](drift-guard/README.md) for the guarded-rewrite loop and prose/code fact-sets.

**The benchmark (methodology / mock smoke):** no third-party packages for the mock run (pure Python 3.9+
stdlib); `pip install -r requirements.txt` only adds optional model SDKs (real runs) and `pytest`.

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

**Iterate only on `bench/tasks/dev/`.** Keep `bench/tasks/heldout/` sealed; score it **once** at the end,
after freezing `bench/preregistration.md`.

## Install as a skill (cross-tool)

```
/plugin marketplace add Vince427/open-cognitive-bench
/plugin install chestertons-shield@open-cognitive-bench
```

## Status (2026-06-04)

PoC scaffold: **41 validated trap tasks** (11 dev + 30 held-out; **5 kinds** — chesterton + goodhart are
benchmarked-ready, while hyrum/security/phantom are **experimental, unvalidated**), all pass
`bench/selfcheck.py`. The harness runs end-to-end on `mock` **and on a real model** via Claude Code subagents
(`bench/pilot/`, no API key).

**Key finding — the real-model pilots changed the plan (`PILOT.md`).** The **single-shot** version of this
benchmark **does not discriminate**: Opus-class and Haiku, every arm (B/C/D/S), scored **0 failures** (a
floor effect) — even a deliberately harder trap. The guardrails target *not investigating large, unfamiliar
code*, which a single-shot toy task can't induce: it either shows the needed fact (trivial) or withholds it
(unfair). That is a **construct ceiling** (`KNOWN_ISSUES.md` V5), not a difficulty knob. A same-day
**agentic, tool-using prototype** (real repo + git history; the agent must investigate) produced the
project's **first arm separation** (bare 1/2 vs skill 0/2 — illustrative, n=2).

So the real remaining work is **not** "just run the API" — it is the **agentic harness** (the only setting
where these guardrails can bite), plus independent held-out authorship and a multi-model run. Full picture in
[`REPORT.md`](REPORT.md).

## Docs
- [`drift-guard/`](drift-guard/README.md) — **the usable deliverable**: executable fact-gate + guarded-rewrite loop + Drift Shield skill.
- [`PAPER.md`](PAPER.md) — arXiv-style methods + negative-results note (the whole arc + the math). **Read this for the honest result.**
- [`DRIFT.md`](DRIFT.md) — iterative-rewrite drift: literature, the DPI/decay math, why the gate (not the prompt) guarantees.
- [`CONCEPTUAL_FOUNDATION.md`](CONCEPTUAL_FOUNDATION.md) — why these guardrails should work (evidence-grounded).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to author trap tasks (and the held-out independence rule).
- [`bench/preregistration.md`](bench/preregistration.md) — freeze before the held-out run.
- [`bench/power_analysis.md`](bench/power_analysis.md) — is the design powered? (LLM-free Monte-Carlo).
- [`RESULTS.md`](RESULTS.md) — results template (fill after the real held-out run).
- [`PILOT.md`](PILOT.md) — real-model pilots (DEV, via Claude Code subagents): a floor effect at every model tier.
- [`REPORT.md`](REPORT.md) — global status report (what's built/tested, the construct-ceiling finding, next steps).
- [`bench/pilot/`](bench/pilot/README.md) — run a real model with NO API key (subagents); provider choice + limits.
- [`bench/agentic/`](bench/agentic/README.md) — the agentic tool-using harness (rounds 1–4) + the drift demo.
- [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md) — QA findings & their status.
- [`BLOG_POST.md`](BLOG_POST.md) — the rationale post (why benchmark guardrails at all).
- [`MULTILANG.md`](MULTILANG.md) — design for multi-language tasks (C#/JS) + the canonical C# trap.

Install (optional): `pip install ".[providers]"` for real-model runs, `".[dev]"` for lint/test. Mock runs need nothing.

## License

MIT (code) — see `LICENSE`. Benchmark data CC BY 4.0.
