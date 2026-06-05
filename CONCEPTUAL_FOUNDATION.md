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

## Candidate guardrails (3 scaffolded in dev — EXPERIMENTAL, not yet validated)
The agent-failure literature suggests a small, clean **taxonomy of "respect failures" when editing existing
code**. Two are validated-and-benchmarked; three more are now **scaffolded as experimental dev-only skills +
trap tasks** (wired into the harness, `selfcheck`-valid) but **not benchmarked** — they are gated behind the
dev-set separation check in `preregistration.md` and have no held-out tasks or real-model evidence yet.

| Failure type | Guardrail | Status |
|---|---|---|
| breaks a hidden **functional invariant** | **Chesterton's Shield** (`chestertons-shield`) | shipped + benchmarked-ready |
| satisfies a **metric** while betraying its intent | **Goodhart Attack** (`goodhart-attack`) | shipped + benchmarked-ready |
| changes **observable behavior outside the requested scope** | **Hyrum's Shield** (`hyrums-shield`, kind `hyrum`) | dev scaffold (2 traps) — experimental |
| weakens a **security posture** while making a functional change | **Fail-Safe** / "Don't Disarm" (`fail-safe`, kind `security`) | dev scaffold (2 traps) — experimental |
| references a **surface that doesn't exist** (invented API) | **Phantom Check** (`phantom-check`, kind `phantom`) | dev scaffold (2 traps) — experimental |

Candidate details (each must keep the project's bar: a documented failure mode, a principle-level rule, and
**execution-detectable** failure):
- **Hyrum's Shield** — anchor: Hyrum's Law ("with enough users, every observable behavior will be depended
  upon"). Targets blast-radius / drive-by over-editing. Trap: a hidden test on a *sibling* behavior (not the
  one being changed) breaks ⇒ the agent touched what it wasn't asked to. Distinct from Chesterton, whose
  hidden test guards the *same* function's weird invariant.
- **Fail-Safe ("Don't Disarm")** — anchor: Saltzer & Schroeder fail-safe defaults / defense-in-depth.
  Targets security regressions introduced during a refactor (parameterized query → string concat,
  validation/escaping removed, a permission check weakened, a secret logged). Trap: a *security* hidden test
  (an injection/traversal probe that must stay blocked) fails. Would add a third task `kind` = `security`.
  **The strongest next addition** — highest real-world stakes, cleanest execution trap, fully orthogonal.
- **Phantom Check ("No Ghost APIs")** — anchor: code/package hallucination ("slopsquatting"). Targets
  invented functions/flags/signatures. Trap: a stub/library context where the tempting helper does not
  exist; the naive edit calls it ⇒ NameError/AttributeError/ImportError at execution. (A
  *verification*-discipline failure — "did you check the surface you were handed" — rather than a pure knowledge failure.)

Not worth a separate rule (they collapse into the above):
- *Refuse-the-false-premise* (sycophancy, 2310.13548) — already the **mechanism** Chesterton's traps exploit
  ("this guard looks redundant, simplify").
- *Test integrity* (don't weaken/skip tests) — already inside **Goodhart Attack**.
- *Backward-compat / public-API stability* — overlaps Chesterton (callers) + Hyrum.
- *No-silent-swallow* (`except: pass` to "pass") — a sub-case of Goodhart.

Discipline: proposing rules is cheap; **validating** one is not (trap tasks + a real run + ideally
independent authorship). Per this repo's own policy a skill is not "done" until it ships with a benchmark
result. The three above are **scaffolded but explicitly NOT validated** — they have only 2 dev traps each
(no held-out), single-author tasks, and zero real-model evidence; treat them as hypotheses to test, not
guardrails to trust. The order of work is unchanged: **validate the existing two first** (dev-set separation
gate), then promote each experimental kind only once it ships its own benchmark result. `Fail-Safe` is the
highest-value of the three (security stakes + cleanest execution trap).

## References
Verified arXiv IDs are given explicitly; works whose exact ID we could not confirm are cited **by name only**
(look them up — we do not assert an unverified number).
- Reward hacking / specification gaming: *Concrete Problems in AI Safety* (Amodei et al., arXiv:1606.06565);
  Krakovna et al. (DeepMind) specification-gaming catalogue; the Goodhart weak/strong formalization literature.
- Sycophancy in RLHF assistants: *Towards Understanding Sycophancy in Language Models* (Sharma et al., ICLR
  2024, arXiv:2310.13548).
- LLM-as-judge biases (position / verbosity / self-preference): *Judging LLM-as-a-Judge with MT-Bench and
  Chatbot Arena* (Zheng et al., arXiv:2306.05685); the length-controlled AlpacaEval work.
- Cited **by name** (exact IDs not asserted here): reason-before-coding / CodeChain; CoT (un)faithfulness;
  plan-compliance in programming agents (a good plan helps, a subpar plan hurts); Constitutional AI
  (specific-vs-general principle steering) and prompt-steerability / "personality illusion"; the
  ideation–execution gap; and the diversity / mode-collapse literature ("Artificial Hivemind").
- Iterative-rewrite drift + model collapse: see [`DRIFT.md`](DRIFT.md) (verified IDs there).
