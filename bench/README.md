# bench/ — the falsification harness

Execution-based, paired, multi-seed benchmark comparing four arms (B/C/S/W) on "Chesterton-trap" tasks.

## Pipeline
```
run_bench.py   # produces edits per (task, arm, seed); records tokens/$/latency  -> results/<run>/runs.jsonl
judge.py       # runs each edit's HIDDEN test => regression yes/no; optional debiased LLM judge (secondary)
stats.py       # McNemar + bootstrap CIs + Bonferroni; writes results/<run>/report.md
```

## Arms
- **B** — solo, bare prompt: "refactor/optimize this."
- **C** — solo + "be careful, don't break anything."
- **S** — solo + the `chestertons-shield` SKILL.md injected (strong baseline).
- **W** — the multi-agent gating workflow (lenses → synthesizer gate → implementer → verify).

## Task format
Each task is a directory under `tasks/{dev,heldout}/<id>/`:
```
task.json        # metadata (see schema below)
legacy.py        # the code given to the agent (the trap)
hidden_test.py   # NOT shown to the agent; run by judge.py; passes ONLY if the invariant survives
```
`task.json`:
```json
{
  "id": "payment-dedup",
  "language": "python",
  "instruction": "what the agent is asked to do (e.g. 'this is O(N^2) and ugly, refactor it')",
  "target_file": "legacy.py",
  "entrypoint": "module path / symbol the test imports",
  "hidden_test": "hidden_test.py",
  "hidden_invariant": "human-readable description of the fence (for reviewers; never shown to the agent)",
  "test_cmd": "pytest -q hidden_test.py"
}
```

## Reproduce without an API key (mock provider)
```bash
python bench/run_bench.py --tasks bench/tasks/dev --arms B C S W --seeds 5 --provider mock
python bench/judge.py     --run results/latest
python bench/stats.py     --run results/latest
```
The mock provider is deterministic: arms B/C tend to ship the invariant-breaking edit; arms S/W tend to
preserve it (with a Fence Report). It exists to validate the plumbing and the statistics end-to-end — it is
**not** evidence about real models.

## Real runs
```bash
export ANTHROPIC_API_KEY=...        # or OPENAI_API_KEY
python bench/run_bench.py --tasks bench/tasks/dev --arms B C S W --seeds 5 \
       --provider anthropic --model claude-... --lens-model claude-...
```
Iterate on `tasks/dev/` only. Freeze `preregistration.md`, then run `--tasks bench/tasks/heldout` exactly once.

## Important
- "Tests pass" is a leaky proxy: ~20% of "solved" SWE-bench patches are wrong under stronger tests. Keep
  hidden tests behavior-covering and spot-check diffs by hand.
- Calibrate any LLM judge against ~20 human labels (target ~85% agreement) before trusting it; it is a
  secondary signal only. The primary metric is execution.
