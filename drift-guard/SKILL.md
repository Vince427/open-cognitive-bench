---
name: drift-shield
description: >-
  Use when EDITING, rewriting, summarizing, "condensing", or "tidying" an existing document or module that may
  be edited again later. Prevents iterative-rewrite drift (the "broken telephone": repeated LLM passes silently
  drop facts, rationale, and constraints). Triggers: "clean this up", "shorten/condense", "rewrite for clarity",
  "summarize", any pass over a file that already carries rules/rationale.
---

# Drift Shield — preserve load-bearing facts across edits

Repeated edits erode a document: each pass drops something it judges unimportant, and the *why* (rationale
comments, ticket/incident refs, legal constraints) goes first. Your job: make that impossible on YOUR pass.
(This is soft prevention — it lowers the loss rate. For a guarantee, pair it with the executable `gate.py`.)

## Procedure (every pass, before returning the file)
1. **Enumerate the load-bearing elements** in the current text:
   - Constants/values **+ their rationale** (limits, magic numbers, ticket/incident refs like "SEC-12").
   - Special-case guards / sentinels (`if x == 0: ...`) and the reason they exist.
   - Security controls (escaping, validation, parameterized queries, access/path checks).
   - Public surface (names, parameters, defaults) other code may depend on.
   - Ordering / idempotency / exact-sum invariants, and any "why" comment explaining them.
2. **Reproduce every one verbatim** in your output — value, guard, control, signature, AND the rationale
   comment. A rationale comment is itself load-bearing: it is how the NEXT editor avoids deleting it.
3. If you cannot tell why something exists, **keep it** (Chesterton's fence). "Looks redundant" is not a reason.
4. Before finishing, **diff against the input**: every constant, guard, control, public name/default, and
   invariant present in the input must still be present. Restore any you dropped.

## Rule
Shorten only where it removes NO load-bearing element or rationale. When in doubt, preserve. Never delete a
guard, a security control, a documented constant, a public default, or an ordering invariant — even if the
surrounding instruction invites "cleanup".
