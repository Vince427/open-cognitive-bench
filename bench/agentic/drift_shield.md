# Drift Shield — preserve load-bearing facts across edits (max anti-drift skill)

You are editing a document/module that may be re-edited many times. Tidying prose, renaming locals, and
shortening are fine. But you must NOT lose or alter any **load-bearing element**. Repeated edits silently
erode these — your job is to make that impossible on your pass.

## Procedure (do this every time, before returning the file)
1. **Enumerate the load-bearing elements** in the current text, across these kinds:
   - **Constants/values + their rationale** (magic numbers, limits, ticket/incident references like "SEC-12").
   - **Special-case guards / sentinels** (e.g. `if x == 0: ...`) and the reason they exist.
   - **Security controls** (escaping, validation, parameterized queries, access/path checks).
   - **Public surface** (function names, parameters, defaults) that other code may depend on.
   - **Ordering / idempotency / exact-sum invariants** and any "why" comment that explains them.
2. **Reproduce every one of them verbatim** in your output — value, guard, control, signature, AND the
   rationale comment. A rationale comment is itself load-bearing: it is how the NEXT editor avoids deleting it.
3. If you cannot tell why something exists, **keep it** (Chesterton's fence). "Looks redundant" is not a reason.
4. Before finishing, **diff against the input**: every constant, guard, control, public name/default, and
   invariant present in the input must still be present. If your edit dropped one, restore it.

## Rule
Shortening is allowed only where it removes NO load-bearing element or rationale. When in doubt, preserve.
Never delete a guard, a security control, a documented constant, a public default, or an ordering invariant —
even if the surrounding text invites "cleanup".
