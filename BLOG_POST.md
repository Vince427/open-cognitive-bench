<!--
Rationale post for Open Cognitive Bench. Unlike a results post, this ships BEFORE the empirical run:
there are NO real-model numbers yet (the harness has only been exercised with a deterministic mock).
Results — whatever they turn out to be — will be published in RESULTS.md, regardless of outcome.
-->

# Don't trust your coding agent's guardrails. Benchmark them.

Ask a coding agent to "refactor this" and it will often make the code *look* better while quietly breaking
a rule nobody wrote down: a composite key that only *looked* redundant, a `ttl == 0` that secretly meant
"never expire," a leap-year branch that seemed like dead weight. Ask it to "make the tests pass" and it may
just hard-code the expected outputs. Two failure modes cause most of the damage:

- **Respect failures** — silently destroying a hidden invariant when editing existing code.
- **Metric-gaming failures** — satisfying the *letter* of a test while betraying its intent (Goodhart's Law).

The fashionable fix is to drop a clever Markdown rules file into the repo and trust it. Here's the
uncomfortable part: **almost nobody measures whether those rules actually work.** Even the 200k-star
agent-skill repos ship zero before/after evidence — a compelling narrative, no number.

## The move nobody makes: try to *falsify* the skill
Open Cognitive Bench packages the two **best-evidenced** guardrails — **Chesterton's Shield** (investigate
*why* code exists before changing it) and **Goodhart Attack** (anticipate how a change games the metric) —
in two forms (a portable **Skill** and an active multi-agent **Workflow**), and ships the **falsifiable
benchmark that decides whether they help.**

The design borrows the discipline of a proper ablation (and, candidly, the spirit of Open Collider's 4-arm
panel):

- **B** baseline · **C** a "be careful" instruction · **D** a length-matched, *ruleless* brief · **S** the
  skill · **W** the workflow.
- The metric is **execution** — a hidden behavior test the edit either preserves or breaks. Not an LLM
  judge's vibe: the literature's *ideation-execution gap* shows "looks better" ≠ "is better."
- **D is the honest falsifier.** Because the skill's prompt is longer than the baseline, a naive "S beats B"
  could just be "more tokens." If **S beats D**, it's the *rule*, not the length.
- Sealed held-out tasks + pre-registration + paired stats (McNemar, bootstrap, Bonferroni) — so we can't
  tune the skill to its own benchmark.

## The open question
Recent work shows a well-engineered single agent can *match* many multi-agent workflows — at 5–10× the cost.
So the question this benchmark exists to answer is sharp and unanswered for code guardrails:

> **Does a cognitive-gating workflow actually beat a strong single-agent + skill at stopping regressions and
> metric-gaming — net of that 5–10× cost?**

This repo is the *instrument*. The answer is one real-model run away.

## Honesty
- **No results yet.** The figures live in `RESULTS.md` and will be published **regardless of outcome** —
  including the skill *not* winning, or the workflow not being worth its cost.
- The "parallel lenses that gate" pattern is **not novel** (Claude Code Ultra, DeepMind Co-Scientist). The
  contribution is the *specific guardrails + the evidence*, not the orchestration.

Repo: `github.com/Vince427/open-cognitive-bench` · Why-it-works: `CONCEPTUAL_FOUNDATION.md`.
