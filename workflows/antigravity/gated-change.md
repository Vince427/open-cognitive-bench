---
description: >-
  Cognitive-gating panel for any change to existing/legacy code. Lens sub-agents investigate in parallel,
  a skeptical synthesizer gates the implementer, and execution verifies the result. Invoke with
  /gated-change before refactors, optimizations, deletions, or "cleanups".
---

# Workflow: gated-change (Antigravity)

> Active multi-agent orchestration. This is NOT a passive skill — the orchestrator pauses and gates on the
> lenses' findings before any code is written. Maps to the Agent Manager (orchestrator → isolated-context
> sub-agents → shared memory → verification artifact).

## 1. Orchestrator — intake
Receive the change goal + target files/diff scope. Write the change context to **shared memory**
(`$SHARED.context`) once, so lenses read it instead of re-parsing the diff.

## 2. Lens sub-agents (isolated context)
// parallel
- **Chesterton-Investigator** — system prompt = `skills/chestertons-shield/SKILL.md`. Output a Fence Report
  to `$SHARED.lenses.chesterton`: the invariant + a cited artifact (blame/caller/test).
- **Goodhart-RedTeam** — system prompt = `skills/goodhart-attack/SKILL.md`. Output a Goodhart Report to
  `$SHARED.lenses.goodhart`: how the planned change could pass tests while breaking intent.

## 3. Skeptical Synthesizer — gate
Read `$SHARED.lenses.*`. Produce `$SHARED.gate`:
- consolidate invariants-to-preserve + divergence risks,
- assign a residual-risk score,
- decision: `PASS` or `BLOCK`.
// if $SHARED.gate.decision == "BLOCK":
    return to step 2 with the invariants to preserve; the implementer is NOT allowed to run yet.

## 4. Implementer
Apply the change, explicitly preserving every invariant in `$SHARED.gate.invariants`. Optimize structure
freely otherwise.

## 5. Verification (artifact)
Run the behavior-covering / hidden tests + re-read the actual diff. Loop results back to the lenses for a
post-implementation pass (catch unforeseen interactions). Attach the test output as the verification artifact.

## Cost note (Sherlock-style selective verification)
Hard-gate only the lenses that are high-signal for the domain (decide this from the benchmark, not a priori).
Let the implementer run speculatively while verification proceeds; roll back on failure. Target: pull the
~5–10× multi-agent overhead down toward ~2–3×.

> **Benchmark note:** the harness (`bench/run_bench.py`, arm `W`) currently implements a **single-pass**
> panel (lenses → synthesizer → implementer). The `// if BLOCK → re-investigate` gate above is the design
> target, not yet implemented in the benchmark (see `KNOWN_ISSUES.md` M4).
