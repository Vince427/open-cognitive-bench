# Prompt — draft a drift-guard fact-set for a document (review once, then the gate enforces it)

Give this to any LLM along with the document. The output is a `facts.txt` for `gate.py --facts`.

---
You are given a document (code or prose). List every **load-bearing fact** a future edit must NOT drop — the
things whose silent loss would be a costly regression:

- constants / limits **and their rationale** (numbers, thresholds, ticket / incident / legal refs — e.g.
  `SEC-12`, `GDPR Art 17`, `100 req/min`);
- special-case guards / sentinels and why they exist;
- security controls (escaping, validation, auth/permission checks, path containment);
- public surface other code depends on (names, parameters, defaults);
- ordering / idempotency / exact-sum invariants.

**Output ONLY the fact-set**, one required item per line:
- a SHORT **literal substring** that must appear in the document, OR
- `re:` followed by a regex for a pattern.

Prefer the most specific, stable token (a ticket id, an exact number, an API name). Be **conservative** —
too few is worse than too many. No prose, no explanation, no code fences.

A human reviews this list once; then `gate.py` enforces every item on every rewrite (and you can verify the
draft against the current doc with `gate.py --facts facts.txt --file <doc>` — every fact should already be present).
