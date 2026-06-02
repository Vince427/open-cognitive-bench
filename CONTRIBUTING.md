# Contributing

The most valuable contribution is **new trap tasks** — especially **independently authored held-out tasks**
(see the independence note below). The harness is pure Python 3.9+ stdlib; no third-party deps for the mock.

## Quick loop
```bash
python bench/selfcheck.py                                   # every task must be a VALID trap
python bench/run_bench.py --tasks bench/tasks/dev --arms B C D S W --seeds 5 --provider mock
python bench/judge.py --run results/latest && python bench/stats.py --run results/latest
```

## Adding a trap task
A task lives in `bench/tasks/<dev|heldout>/<id>/`. Two kinds:

### chesterton (failure = regression)
The agent is given **correct-but-ugly** code and asked to refactor; failure = its edit breaks a hidden invariant.
- `task.json`: `{"id","kind":"chesterton","language":"python","instruction","target_file":"legacy.py","hidden_test":"hidden_test.py","hidden_invariant","test_cmd"}`
- `legacy.py`: the trap — looks refactorable, but a "weird" asymmetry encodes a real invariant.
- `hidden_test.py`: plain `assert`-based `test_*` functions that pass for the original and **fail** for the naive rewrite.
- Mock answer: add `"<id>": "<naive bad rewrite>"` to `NEW_BAD_REWRITES` in `bench/extra_mock_answers.py`
  (mock simulator only; unused for real runs).

### goodhart (failure = metric-gaming / "hack")
The agent is given a **stub + a deliberately weak visible test** to make pass; failure = the visible test
passes but a held-out hidden behavior test fails.
- `task.json` adds `"kind":"goodhart"` and `"visible_test":"visible_test.py"`.
- `legacy.py`: a stub (e.g. `raise NotImplementedError`).
- `visible_test.py`: weak/gameable (few cases). `hidden_test.py`: strong, behavior-covering.
- Mock answer: add `"<id>": {"correct": "...", "hacked": "..."}` to `NEW_GOODHART_IMPLS` in
  `bench/extra_mock_answers.py` (the hacked impl must pass visible and fail hidden; correct passes both).

**Then run `python bench/selfcheck.py` — your task must print `VALID TRAP`.** Keep test cases integer-exact
where possible (avoid float-equality flakiness). No `"""docstrings"""` collisions; use `#` comments.

## Held-out independence (important)
`bench/tasks/heldout/` is **sealed** and scored once. For a credible/publishable result:
- Held-out tasks should be authored by **someone other than the skill author**.
- Do **not** read held-out `hidden_test.py` / `hidden_invariant` while tuning a skill on the dev set.
- Prefer invariants/domains that post-date model training cutoffs.

## Adding a skill
A skill is `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description` for auto-trigger). Keep it
evidence-bound: tie the rule to a checkable artifact or action (see `CONCEPTUAL_FOUNDATION.md`). A new skill
is only "done" once it ships with a benchmark result — including a negative one.

## Conventions
- Line endings: LF (`.gitattributes` enforces it). CI runs `selfcheck` + the mock pipeline on every push.
- Don't commit run outputs (`results/run-*/` is git-ignored); publish a curated run with `git add -f`.
- Open a PR with: what you added, `selfcheck` output, and (for skills) a benchmark delta.
