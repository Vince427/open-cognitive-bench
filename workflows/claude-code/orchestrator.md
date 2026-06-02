# Workflow: gated-change (Claude Code)

Claude Code has no declarative workflow file; orchestration is **procedural** via the Agent/Task tool. This
document is the orchestrator's operating contract. The benchmark's arm **W** implements exactly this in
`bench/run_bench.py` (`_run_workflow`).

## Orchestrator loop
1. **Intake.** Read the change goal + target file. Build a single shared-context string (the file + the task).
2. **Spawn lenses in parallel** — in ONE message, issue multiple `Agent` tool calls (they dispatch
   concurrently):
   - Lens A — **Chesterton-Investigator**: subagent prompt = contents of `skills/chestertons-shield/SKILL.md`
     + the shared context. Returns a Fence Report (invariant + cited artifact).
   - Lens B — **Goodhart-RedTeam**: subagent prompt = `skills/goodhart-attack/SKILL.md` + shared context.
     Returns a Goodhart Report.
3. **Gate (synthesizer).** A skeptical synthesizer subagent reads both reports and returns
   `{decision: PASS|BLOCK, invariants: [...], risks: [...]}`. If `BLOCK`, re-run step 2 with the invariants
   surfaced; do not let the implementer run.
4. **Implement.** The implementer subagent receives the original task **plus** the gate's invariants list and
   produces the edited file.
5. **Verify.** Run the hidden/behavior-covering tests; on failure, return the trace to the lenses for one
   more pass.

## Notes
- Each subagent runs in an isolated context window (clean — no parent history), like Antigravity sub-agents.
- Concurrency cap and cost: lenses run concurrently, so wall-clock ≈ the slowest lens, but **token cost ≈ Σ
  lenses + synthesizer + implementer** — this is the 5–10× multiplier the benchmark measures against arm S.
- Keep the synthesizer's output short and structured; it is the only cross-lens state.
- **Benchmark note:** arm `W` in `bench/run_bench.py` runs a **single pass** (lenses → synth → implementer);
  the BLOCK / re-investigate loop in step 3 is the design target, not yet implemented (`KNOWN_ISSUES.md` M4).
