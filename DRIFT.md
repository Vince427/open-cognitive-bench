# Iterative-rewrite drift: why re-editing a document with an LLM loses information, and what provably stops it

**Companion note to `PAPER.md`, v0.1 (2026-06-04).** Grounds the project's clearest positive (the
`bench/agentic/` drift demo) in the literature and gives the math. The arXiv IDs below were checked against
arXiv; one prose mention (a translation-chain example) is attributed loosely and marked as such.

---

## 1. The phenomenon — and a distinction the literature insists on
Two failure modes are routinely conflated; only the second is ours.

- **Model collapse (recursion at *training* time).** Train model *k+1* on model *k*'s outputs, repeat:
  quality degrades, the **tails of the distribution vanish**, the defect is irreversible. Shumailov et al.,
  *The Curse of Recursion: Training on Generated Data Makes Models Forget* ([arXiv:2305.17493](https://arxiv.org/abs/2305.17493),
  2023) and *AI models collapse when trained on recursively generated data*
  ([Nature 2024](https://www.nature.com/articles/s41586-024-07566-y)). **Not our case** — it's about the model.
- **Broken-telephone drift (recursion at *inference* time).** Pass one *artifact* through an LLM repeatedly
  (paraphrase / rewrite / "condense") and information distorts and disappears. *LLM as a Broken Telephone:
  Iterative Generation Distorts Information* ([arXiv:2502.20258](https://arxiv.org/pdf/2502.20258)); a
  30-iteration, 17-model paraphrase study ([Joshua8.AI](https://joshua8.ai/llm-telephone-game-semantic-drift/));
  and (reported in the iterative-translation literature, attribution not independently confirmed) a long
  translation chain that drifted a news story off-topic. For code specifically: *SCAFFOLD-CEGIS: Preventing Latent Security Degradation in LLM-Driven
  Iterative Code Refinement* ([arXiv:2603.08520](https://arxiv.org/pdf/2603.08520)). **This is exactly our
  case:** a doc/module re-edited pass after pass by an agent.

Literature consensus we build on: degradation under pure rephrasing is **near-inevitable**, but **mitigable
with temperature=0 and highly restrictive prompts**, and security/spec constraints **drift away** under
iterative optimization unless explicitly anchored.

## 2. Why drift is a theorem, not a bug (the math)

**(a) The Data-Processing-Inequality argument.** An unguided rewrite chain is a Markov chain
$D_0 \to D_1 \to \dots \to D_n$ (each version is produced from the previous one only). For any function of the
source — in particular the set of *load-bearing facts* $F\subseteq D_0$ — the Data Processing Inequality gives
$$I(D_0; D_n)\;\le\;I(D_0; D_{n-1})\;\le\;\dots\;\le\;I(D_0; D_1).$$
Information the chain retains about the original is **monotonically non-increasing**. Drift is not a model
defect; it is forced by the *topology* (pure re-generation from the latest copy). **The only way out is to
stop being a pure Markov chain** — re-inject the source / verify against it — which is precisely what a
re-applied rule or an external check does.

**(b) A survival / decay model that fits the demo.** Let the document carry $K$ load-bearing facts. Treat fact
$i$ as "alive" until dropped; once dropped it is not re-derived (absorbing). If each pass drops a *live* fact
$i$ with hazard $p_i$, then
$$\Pr[\text{fact }i\text{ alive after }n\text{ passes}] = (1-p_i)^n,\qquad
\mathbb{E}[S_n] = \sum_{i=1}^{K}(1-p_i)^n.$$
Homogeneous case $p_i=p$: $\mathbb{E}[S_n]=K(1-p)^n$ — **exponential decay**, half-life
$n_{1/2}=\ln 2/(-\ln(1-p))$. Real documents are **heterogeneous**: "soft" facts (rationale comments,
*why*-knowledge) have high hazard $p_\text{soft}$ (a "condense" pass deletes them at once); "hard" facts (code
behavior pinned by structure) have low $p_\text{hard}$.

## 3. Our demonstration (empirical illustration)
Seed `drift_seed.py`: $K=5$ load-bearing facts spanning the guardrail taxonomy — a legal constant + its
**SEC-12 rationale** (soft), a `ttl==0` sentinel / INC-2231, an `html.escape` XSS control, a public `sep`
default, a first-seen-order invariant. $n$ passes of "**aggressively condense this**" (a *fresh* Haiku
subagent per pass — a faithful Markov chain), bare vs the maximal **Drift Shield** skill re-applied each pass.
Verifier: `drift_check.py` (executable; counts surviving facts).

| pass $n$ | bare $S_n$ | + Drift Shield $S_n$ |
|---|---|---|
| 0 | 5 | 5 |
| 1 | **4** (SEC-12 rationale gone) | 5 |
| 2–5 | **4**, code degrades to lambdas (`...e["ttl"]>0and...`) | **5** (clean, rationale kept inline) |

This is the heterogeneous model with **one soft fact** ($p_\text{soft}\approx1$ — lost on pass 1) and **four
hard facts** ($p_\text{hard}\approx0$ over 5 passes): $S_n^\text{bare}\approx 4 + (1-1)^n = 4$ for $n\ge1$, vs
$S_n^\text{skill}=5$. The *why* — the most fragile, least test-protected knowledge — drifts **first and
fastest**, exactly as the broken-telephone literature predicts.

## 4. What the math says each intervention can and cannot do
| Intervention | Effect on the dynamics | Math | Guarantee? |
|---|---|---|---|
| **Bare** | pure Markov chain | $S_n=\sum_i(1-p_i)^n\to 0$ | none — DPI forces monotone loss |
| **Skill** (Drift Shield, *re-applied each pass*) | lowers hazards $p_i\to q_i\ll p_i$ | $S_n=\sum_i(1-q_i)^n$ | **delays, doesn't defeat** — still Markov, so DPI still bites; as $n\to\infty$, $q_i>0\Rightarrow$ eventual loss. (In the 5-pass demo $q_i\approx0$, so it held 5/5.) |
| **Gate** (verify vs the fact-set each pass; **reject/revert** a lossy pass) | conditions each step on a verifier $V$ → no longer a pure degrading chain | the set $\{D: V(D)=\text{all }K\text{ facts}\}$ is **invariant/absorbing** under the gated map ⇒ $S_n=K\ \forall n$ | **yes** (cost: expected retries per accepted pass ≈ geometric in the per-pass success rate) |

**Key formal statement.** Re-applying the rule *reduces the decay rate*; only the **gate makes "all facts
preserved" a fixed point** of the rewriting dynamics — because it is the only intervention that re-introduces
source information (escapes the DPI). This is the rigorous reason "the skill is soft prevention, the gate is
the guarantee," and it matches **SCAFFOLD-CEGIS**, whose counterexample-guided verifier loop prevents
security degradation in iterative code refinement.

## 5. Literature vs our solution
| | What it studies | What it offers | Relation to us |
|---|---|---|---|
| Curse of Recursion / Nature (Shumailov) | training-time collapse | a *warning* (don't train on generated data) | different mechanism; we cite it to **disambiguate** |
| LLM as a Broken Telephone (2502.20258) | inference-time iterative distortion | quantifies/diagnoses the drift | **our exact phenomenon**, documented |
| Telephone-game 30-iter study | drift across 17 models | measurement at scale | shows drift is general; ours is a 5-pass code instance |
| SCAFFOLD-CEGIS (2603.08520) | security loss in iterative code refinement | a verifier loop that prevents it | **same family as our gate** — independent support |
| **This work** | drift on **load-bearing facts** in code/docs | a *guardrail skill* (rate reducer) **+ an executable fact-gate** (guarantee), and the DPI/decay framing | combines mitigation (restrictive prompt) + enforcement (verifier) and **measures both** |

Our marginal contribution is modest but real: (i) framing drift via the **DPI** (drift is a theorem; only
re-injection/verification escapes it); (ii) a concrete **executable fact-gate** for arbitrary docs/code, with
a falsifiable check; (iii) an honest measurement showing the **skill delays, the gate guarantees**.

## 6. Honest limits & what to build
n=1 chain per arm, one model (Haiku), facts hand-picked to match the rule, single author — a **clean
demonstration, not a powered study**. The bare loss here was mostly the *rationale* (comments); code behavior
mostly survived (a longer run / weaker model would erode code too — we already saw a `>0and` SyntaxWarning).
**Build:** `drift-guard` = the Drift Shield skill **+** a `drift_check`-style gate that (a) extracts the
fact-set once, (b) re-runs after every LLM pass, (c) **rejects/reverts** any pass that drops a fact. The skill
keeps the *rationale* alive for humans; the gate keeps the *facts* alive for certain.

## References (arXiv IDs checked against arxiv.org)
- Shumailov et al., *The Curse of Recursion* — [arXiv:2305.17493](https://arxiv.org/abs/2305.17493); Nature 2024 — [s41586-024-07566-y](https://www.nature.com/articles/s41586-024-07566-y).
- *LLM as a Broken Telephone* — [arXiv:2502.20258](https://arxiv.org/pdf/2502.20258).
- Telephone-game semantic-drift study — [Joshua8.AI](https://joshua8.ai/llm-telephone-game-semantic-drift/).
- *SCAFFOLD-CEGIS* (security degradation in iterative code refinement) — [arXiv:2603.08520](https://arxiv.org/pdf/2603.08520).
- *FACT: Iterative Context Rewriting for Multi-fact Retrieval* — [arXiv:2410.21012](https://arxiv.org/pdf/2410.21012).
