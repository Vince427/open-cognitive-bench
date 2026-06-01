---
name: chestertons-shield
description: >-
  Use BEFORE modifying, refactoring, deleting, or "cleaning up" any existing/legacy code.
  Forces an evidence-based investigation of WHY the current code exists (Chesterton's Fence) and
  anchors it to a verifiable artifact before any change. Triggers: refactor, optimize, simplify,
  remove dead code, "this code is ugly", "clean this up".
---

# Chesterton's Shield

## Rule
You may NOT modify, simplify, or delete existing code until you have produced a **Fence Report** proving
you understand why it exists — or proving you searched and found no reason.

## Procedure (evidence, not prose) — run these and cite the results
1. `git blame` / `git log -p` on the lines → date, author, commit message.
2. Find ALL callers (grep / symbol search) → who depends on this behavior?
3. Read the tests covering this code → which edge cases do they lock in?
4. Spot the "weird" asymmetry (nested conditions, special cases, odd comments) → that's usually where the
   hidden invariant lives. State the invariant hypothesis explicitly, then confirm it from 1–3.

## Fence Report (required artifact — paste BEFORE the diff)
- **Likely reason it exists:** <1–2 sentences, WITH a citation: commit hash / caller / test name>
- **Invariant to preserve:** <concrete; "none found" is a valid answer ONLY IF facts 1–4 are provided>
- **Evidence:** <a specific blame line / test name / caller — not a generality>
- **Decision:** preserve the invariant and optimize ONLY the structure | refuse the change |
  proceed while explicitly flagging that no reason was found after checking 1–4

## Guardrails
- A sloppy investigation is WORSE than none (empirically: a subpar plan hurts more than no plan). If you
  cannot cite a concrete fact for 1–4, say so — do not fabricate a plausible-sounding justification.
- An eloquent "why this fence exists" narrative is NOT proof you actually checked. Always anchor to a
  citable artifact (the call-site / test / commit you found).
- Optimizing performance/readability IS encouraged once the invariant is mapped — e.g. replace an O(N²)
  loop with a `HashSet` keyed on the **correct composite key**, not on a sub-key that collapses distinct items.
