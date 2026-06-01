# Held-out tasks — SEALED

⚠️ **Do not iterate on these while developing a skill.** This set is scored **once**, at the end, after
`bench/preregistration.md` is frozen and committed. It is the only defense against tuning a skill to its
own benchmark.

Rules:
- Tasks here MUST be authored by **someone other than the skill author** (separation of concerns).
- Prefer invariants/domains that post-date model training cutoffs (anti-contamination).
- Target ≥ 30 tasks before drawing conclusions; the single `money-rounding` task here is a format seed only.
- The skill author should not read the `hidden_test.py` / `hidden_invariant` of held-out tasks before the run.

Add new traps following the same format as `tasks/dev/<id>/` (task.json + legacy.py + hidden_test.py).
Good families: cache invalidation, firmware-bug workarounds, order-of-operations / locking, monetary
rounding, timezone/DST edge cases, retry/idempotency keys, off-by-one guards.
