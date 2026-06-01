# AGENTS.md — Open Cognitive Bench

Cross-tool entry point. Antigravity, Claude Code, Cursor and Codex read this file. It activates the
**portable Skills** in this repo. (The multi-agent **Workflows** in `workflows/` are tool-specific and are
invoked explicitly — see that folder.)

## Active guardrails (Skills)

### Chesterton's Shield  →  `skills/chestertons-shield/SKILL.md`
Before modifying, refactoring, deleting or "cleaning up" any existing/legacy code, you MUST produce a
**Fence Report** proving you understand *why* the current code exists (or proving you searched and found
nothing), anchored to a verifiable artifact (a `git blame` line, a caller, or a test). A sloppy
investigation is worse than none — cite concrete facts, never invent a plausible justification.

### Goodhart Attack  →  `skills/goodhart-attack/SKILL.md`
Before trusting that a change "passes", red-team how it could satisfy the letter of the metric/test while
betraying its intent. Prefer a generic "surface where the metric and the goal diverge" stance over a
brittle list of specific exploits.

## Project conventions
- Iterate on benchmark tasks only in `bench/tasks/dev/`. **Never read or modify** `bench/tasks/heldout/`
  while developing a skill — it is sealed for the final, single scored run.
- Every guardrail must ship with a reproducible benchmark result before any claim is made about it.
