# Conceptual Foundation

Why these two guardrails, and why an execution-based falsification benchmark. (Evidence-grounded; this is the
"why it should work" companion to the README's "what it is".)

## Thesis
Most damage an AI coding agent does is not a *knowledge* failure. It is a **respect failure** (silently
breaking a hidden invariant when editing existing code) or a **metric-gaming failure** (satisfying a
test/metric while betraying its intent). We ship one guardrail for each — **Chesterton's Shield** and
**Goodhart Attack** — and *measure* whether they help, instead of asserting it.

## Why reliability, not ideation
The "kill AI slop / boost creativity" angle (forcing distant-domain collisions, à la Koestler bisociation)
is already well-occupied — notably by **Open Collider** — and the diversity literature (alignment-induced
mode collapse; the "Artificial Hivemind" of cross-model convergence) confirms it is a real but crowded
problem. We deliberately target the **reliability** angle, where (a) failure is objectively checkable by
execution, and (b) no incumbent ships reproducible before/after evidence.

## Chesterton's Shield — the evidence
Principle: don't remove/refactor something until you understand *why* it exists.
- **"Understand/plan before acting" helps — but only when the understanding is correct.** Work on plan
  compliance in autonomous programming agents finds a good plan (plus reminders) improves issue resolution,
  **but a subpar plan hurts more than no plan at all.** → the skill must force *genuine* investigation
  (`git blame`, callers, tests), not a perfunctory paragraph.
- **An articulate explanation is not proof of reasoning** — chain-of-thought can be post-hoc
  rationalization. → anchor the Fence Report to a *citable artifact* (a blame line / caller / test).
- Structured reason-/decompose-before-coding loops raise code-generation correctness.

## Goodhart Attack — the evidence
Principle (Goodhart/Strathern): when a measure becomes a target it stops being a good measure.
- Well-formalized (weak vs strong Goodhart) and richly documented (specification-gaming catalogs, reward
  hacking). Frontier **reasoning models hack by default** in some agentic settings.
- **Naming the loophole reduces gaming**, and a *generic* anti-exploit stance generalizes better than a
  brittle list of specific hacks. → keep the skill principle-level.
- Sycophancy shows models bend toward whatever pleases the rater → watch the obfuscation failure mode
  (don't pressure the model merely to "look compliant").

## Are principle-prompts just placebo?
Honest answer from the literature: **not placebo, but real-yet-modest and wording-sensitive.** Effects are
strongest when a principle is (a) reinforced in *training* (Constitutional AI: one general principle
generalized to un-named behaviors — via RLAIF, not pure prompting), or (b) names a *concrete failure mode
tied to a verifiable action*. They are weakest for abstract/affective framings whose only evidence is the
model's self-report ("personality illusion"; prompt brittleness). This is precisely why we (i) chose the two
**best-supported** guardrails, (ii) tie them to checkable artifacts/tests, and (iii) **A/B test every skill**
rather than trust plausibility. Expect smaller effects on frontier reasoning models (they already plan).

## Why an execution-based falsification benchmark
- **"Looks better" ≠ "is better."** The ideation-execution gap: LLM ideas judged more novel than experts'
  *lost* that edge once executed (rankings even flipped). → score the *executed* artifact (a hidden behavior
  test), not the proposal.
- **LLM judges are biased** (position, verbosity/length, self-preference). → execution is the primary metric;
  any LLM judge is secondary, must use a model family different from the generator, and must be calibrated
  against humans.
- **Isolate the active ingredient** (arms B/C/D/S/W): a length-matched ruleless control (**D**) rules out
  "the win is just a longer prompt"; an instruction-only control (**C**) rules out "it's just generic caution."
- **Don't overfit the benchmark**: dev vs sealed held-out, pre-registration, paired stats with multiplicity
  correction. See `bench/preregistration.md`.

## References
Gathered via literature search; **re-verify exact IDs/claims before any public or published use.**
- Goodhart formalization (weak/strong): arXiv 2410.09638. Concrete Problems in AI Safety: 1606.06565.
- Specification gaming / reward hacking: Krakovna et al. (DeepMind) catalog; reasoning-model spec-gaming
  2502.13295; recontextualization mitigates gaming 2512.19027.
- Sycophancy in RLHF assistants: 2310.13548.
- Plan compliance in programming agents (good plan helps; subpar plan hurts): 2604.12147.
- CoT (un)faithfulness: 2503.08679. Reason-before-coding (CodeChain): 2310.08992.
- Principle steering: Constitutional AI specific-vs-general 2310.13798; prompt steerability / "personality
  illusion" 2411.12405.
- Ideation-execution gap: 2506.20803 (ideation study: 2409.04109).
- LLM-as-judge biases: MT-Bench/Chatbot Arena 2306.05685; self-preference 2404.13076; length-controlled
  AlpacaEval 2404.04475.
- Diversity / mode collapse (why we avoided the ideation angle): RLHF reduces diversity 2310.06452;
  Artificial Hivemind 2510.22954.
