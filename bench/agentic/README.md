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

## First run (Haiku, 3 fixtures × B/C/S × 2 seeds = 18 tooled agents, 2026-06-04)

| fixture | B | C | S | discovery channel |
|---|---|---|---|---|
| cache-ttl | **0.50** | 0.00 | 0.00 | git blame (INC-2231 commit) — true investigation trap |
| merge-none | 0.00 | 0.00 | 0.00 | (intended: caller) — see flaw below |
| safe-divide | **0.50** | 0.00 | 0.00 | NULL CONTROL (obvious in-file comment) |
| **pooled** | **2/6 = .33** | **0/6** | **0/6** | McNemar S-vs-B p=0.50 (n10/n01 0/2) — **not significant** |

## Honest reading (the controls did their job — no false positive)
- **The construct works**: it produces real failures (single-shot never did). Tool-use rose to 6–20 calls.
- **S did NOT beat C** (both 0/6): no evidence the Chesterton skill helps *beyond generic "be careful"* here.
- **One bare failure is the null control** (`safe-divide B`: removed an obviously-commented guard) → that's
  model *carelessness*, not lack of investigation. So B's failures are not cleanly an investigation story.
- **`merge-none` didn't test investigation**: bare agents kept the `if v is not None` logic because it is
  *visible in the edited function itself* — the invariant wasn't actually withheld. **Fixture-design flaw**:
  a real investigation trap needs the invariant ABSENT from the edited file (like `cache-ttl`, where the WHY
  lives only in git blame). `cache-ttl` is the only clean trap here, and there B failed 1/2 vs S 0/2 — suggestive, n=2.
- **Not significant** (n=6/arm). This is a prototype, not a result.

## Next (to make this a real measurement)
1. Rebuild fixtures so the invariant is **never visible in the edited file** (caller-only / git-only), like
   `cache-ttl`. Drop or redesign `merge-none`.
2. Many more fixtures + seeds + a 2nd model; report S-vs-C (skill vs caution) as the primary contrast.
3. **Independent author** for the fixtures (the single-author bias is unaddressed).
4. A bare-arm "rushed" control to bound trap fairness.
