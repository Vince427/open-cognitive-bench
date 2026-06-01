# Held-out tasks — SEALED

⚠️ **Do not iterate on these while developing a skill.** This set is scored **once**, at the end, after
`bench/preregistration.md` is frozen and committed. It is the only defense against tuning a skill to its
own benchmark.

This set currently holds **30 tasks** (18 chesterton + 12 goodhart) — enough for statistical power
(30 tasks × ≥5 seeds × 2 models ≈ 300+ datapoints/arm). All are validated by `bench/selfcheck.py`.

Rules / caveats:
- Ideally these MUST be authored by **someone other than the skill author** (separation of concerns).
  These seed tasks were authored alongside the skills, so for a *publishable* result either (a) have an
  independent contributor add/replace tasks, or (b) state this limitation explicitly.
- Prefer invariants/domains that post-date model training cutoffs (anti-contamination).
- The skill author should not look at held-out hidden tests while tuning a skill on the dev set.

Add new traps following the same format. Good families already covered: dedup/composite keys, cache TTL
sentinels, idempotency, business-day/leap-year date math, monetary rounding, pagination clamping, version
comparison, quote-aware parsing (chesterton); and hard-coding / lazy-implementation gaming of weak visible
tests (goodhart). Still wanted: timezone/DST, locking/order-of-operations, regex catastrophic backtracking.
