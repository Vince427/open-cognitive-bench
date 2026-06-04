# Agentic harness (V2) — adversarial prototype

The single-shot benchmark can't measure these guardrails (`PILOT.md`, finding V5): a competent model either
gets the fact handed to it (trivial) or it's withheld (unfair). This harness puts the invariant in a **real
repo with git history**, gives the agent **tools**, and asks whether the *skill* makes it investigate. It is
built with **anti-self-deception controls** because the same author wrote the skill, the fixtures, and the judge.

## Run it
```
bash bench/agentic/build.sh            # builds 3 fixtures + work copies under results/_v2b (git-ignored)
# dispatch one tooled subagent per results/_v2b/work/<fixture>__<arm>__s<seed>/ (see protocol below)
python bench/agentic/score.py haiku    # fixture x arm failure matrix + judgments.jsonl
python bench/stats.py --run results/latest
```
Protocol: each subagent gets the repo path + the fixture instruction + tools (read/grep/git/run-tests),
edits the target in place. Arm **B** = task only; **C** = + "be careful not to break behavior"; **S** = +
`chestertons-shield/SKILL.md` ("investigate why before changing").

## Anti-self-deception controls (the point)
- **Arm C (generic caution)** alongside S: if S only matches C, the *skill* adds nothing beyond "be careful."
- **Null-control fixture (safe-divide)**: the invariant is OBVIOUS in-file (a comment) — no investigation
  needed. If S "beats" B here, the bare arm is being sandbagged, not out-investigated.
- Diverse discovery channels per fixture (git blame vs caller vs in-file).

## Round 2 — hardened fixtures, larger (Haiku, 4 fixtures × B/C/S × 3 seeds = 36 tooled agents, 2026-06-04)

Replaced `merge-none` (its invariant was visible in the edited function) with `retry-idem` (git blame +
caller) and `money-split` (existing test); kept `cache-ttl` (git blame) and `safe-divide` (null control).

| fixture | B | C | S | channel |
|---|---|---|---|---|
| cache-ttl | 0.33 | 0.00 | 0.00 | git blame |
| retry-idem | 0.33 | 0.00 | 0.33 | git blame + caller |
| money-split | 0.33 | 0.00 | 0.00 | existing test |
| safe-divide | 0.33 | 0.00 | 0.00 | NULL CONTROL |
| **pooled** | **4/12 = .33** | **0/12** | **1/12 = .08** | |

### 🔴 This round is CONTAMINATED — read before trusting any number
The work copies were built **under the project tree** (`results/_v2b/`), so tooled agents **grepped up to the
real benchmark** and read the answers: transcripts show them citing `bench/tasks/heldout/.../task.json`
(the `hidden_invariant`!), `hidden_test.py`, even `CLAUDE.md` ("this is a Chesterton's Shield trap"). Both
arms could read the answer key, so the numbers are not a clean test of investigation. **Fixed in tooling:**
`build.sh`/`score.py` now build fixtures **outside the repo** (`$OCB_AGENTIC`, default `~/ocb_agentic`).
A clean re-run is required before any of the numbers above are quoted.

### What still survives the contamination (two robust signals)
- **`C` (generic caution) ≥ `S` (skill)**: C 0/12, S 1/12. Across both rounds the skill shows **no advantage
  over plain "be careful."** That is the central anti-self-deception result.
- **`B` fails the NULL CONTROL as often as the real traps** (all four fixtures 0.33). So the bare arm's
  failures are largely **baseline model carelessness**, not "didn't investigate" — the investigation story is
  not supported. (`B` ~1/3 everywhere looks like a flat competence floor, not a trap-specific effect.)

## Next (to make this a real measurement)
1. **Isolation (done in tooling, needs a clean re-run):** fixtures out-of-tree so agents can't read the repo.
2. Restrict agent tools to the fixture dir; add a bare-arm "rushed" control to bound trap fairness.
3. Many more fixtures/seeds + a 2nd model; **report S-vs-C as the primary contrast** (it's the one that matters).
4. **Independent author** for fixtures + skill (single-author bias unaddressed) — the load-bearing fix.
5. Watch the null control every round: if a guardrail ever "helps" there, the setup is biased.
