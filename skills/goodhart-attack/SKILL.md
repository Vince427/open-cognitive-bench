---
name: goodhart-attack
description: >-
  Use BEFORE trusting that a change "passes" its tests/metrics, and when designing acceptance criteria.
  Red-teams how a change can satisfy the LETTER of a metric while betraying its INTENT (Goodhart's Law /
  reward hacking). Triggers: "make the tests pass", "hit the coverage target", "optimize the KPI",
  defining acceptance criteria, reviewing a diff that suspiciously just-passes.
---

# Goodhart Attack

## Rule
"When a measure becomes a target, it ceases to be a good measure." Before accepting that a change meets a
metric, spend one explicit pass trying to BREAK the link between the metric and the real goal.

## Procedure
1. Name the **true goal** behind each metric/test in one sentence (what the metric is a *proxy* for).
2. Adopt an adversarial stance: *how would a lazy or cynical optimizer pass this metric while defeating the
   goal?* (hard-coding expected outputs, weakening an assertion, deleting/skipping a test, special-casing
   the test input, narrowing a type to dodge a check, gaming a coverage counter with no-op tests).
3. Check the actual diff for any of these tells.
4. State, generically, **where the metric and the goal can diverge** — do not just enumerate today's hacks
   (a generic anti-exploit framing generalizes better than a brittle hack list).

## Goodhart Report (artifact)
- **Metric → true goal:** <metric> is a proxy for <goal>.
- **Most likely divergence:** <the cheapest way to pass while failing the goal>.
- **Found in this diff? :** yes/no, with the specific line.
- **Recommendation:** strengthen the check / add a behavior-covering assertion / reject.

## Guardrails
- Don't apply optimization pressure to "look compliant" — that pushes gaming underground (obfuscated
  reward hacking). The aim is to surface divergence, not to coach evasion.
- Prefer adding a behavior-covering test over arguing in prose.
