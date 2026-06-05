# drift-guard — stop LLMs from silently dropping facts when they re-edit a document

Repeatedly running a file/doc through an LLM (rewrite, "condense", summarize, agentic refactor) erodes it:
each pass drops something it judges unimportant, and the *why* (rationale, ticket refs, legal constraints)
goes first. This is **iterative-rewrite drift** (a.k.a. "broken telephone"; see [`../DRIFT.md`](../DRIFT.md)
for the literature + math). drift-guard ships **two layers**:

| Layer | File | What it is | Strength |
|---|---|---|---|
| **Gate** (the substance) | `gate.py` | an **executable** check, re-run after every pass; **rejects** any pass that drops a load-bearing fact | **guarantee** — "all facts preserved" becomes an invariant of the loop |
| **Skill** (the soft layer) | `SKILL.md` | a prompt ("Drift Shield") telling the editor to preserve every load-bearing element | *delays* drift; does not defeat it (a prompt is still a lossy step — DPI) |

> **Lead with the gate.** A prompt alone is too weak to promise anything: the Data-Processing-Inequality says
> an unguided rewrite chain can only *lose* information about the source (`../DRIFT.md` §2). Only re-checking
> against the source — the gate — escapes that. The skill lowers the loss rate; the gate enforces zero loss.

## Does this actually work? (plain language — no math needed)
Three separate claims, and they are NOT equally solid. Honestly:

1. **"If you don't check, repeated rewriting loses information."** — **Solid.** This rests on a standard,
   textbook result (the *Data Processing Inequality*): if each version is made only from the previous one,
   you can never *recover* what an earlier pass dropped. It's not something we invented; it's established and
   not controversial. Plus the literature measures it (`../DRIFT.md` §1).
2. **"The gate guarantees the facts you listed survive."** — **Certain, but the reasoning is simple, not deep
   math.** It's just: *you only keep a new version if it still contains every listed fact; therefore every
   kept version contains them.* Airtight logic. Three real limits, not math ones: (a) it only protects the
   facts **you wrote down** (a fact you forgot isn't guarded); (b) a pass can keep getting rejected, so you
   may retry (a cost, not a failure); (c) **`--facts` checks string *presence*, not *meaning*** — a rewrite
   that keeps the words but negates them (e.g. "data is **NOT** retained for 90 days") still passes, because
   the substring "90 days" is present. So `--facts` guards *the phrase survives*, not *the claim stays true*.
   Two deterministic (guarantee-preserving) fixes: (i) for code, use the **`--checks`** path (a `checks.py`
   module that asserts behavior, e.g. `is_expired(...) is False`, which a negation cannot satisfy); (ii) for
   prose, add an **anti-fact** — a `not:` line for a phrase that must be ABSENT (e.g. `not:NOT retained`, or
   `not re:` for a regex) — which catches the specific negation. What you *cannot* do deterministically is
   verify arbitrary meaning-preservation; that needs an ML judge, which can only *reduce* (it is non-
   deterministic and DPI-bound, exactly like the skill — never a guarantee). See "Prior art" below.
3. **"The skill (prompt) reduces drift."** — **Observed, NOT proven.** Our demo and the literature show a
   restrictive prompt *helps* — but the math above says a prompt **cannot** guarantee it (a prompt is still a
   lossy step). So treat the skill as "helps, fewer rejects," never as a promise.

**Bottom line for you:** the **gate = a real guarantee** (on what you check), by simple logic; the **skill =
a helpful but unproven nudge**; **drift-without-checks = backed by real, established theory.** So "CI (gate)
+ skill reduces drift" is honest — with the gate doing the *guaranteeing* and the skill doing the *reducing*.

> **A genuine ask (I am stating this honestly):** I am summarizing the math, not delivering a peer-reviewed
> proof. What would *really* strengthen this: someone qualified formally modeling the quantitative decay and
> the skill's effect at scale (more models, many seeds, a proper statistical test), and checking my DPI
> framing. Today it is: **one standard theorem (qualitative) + one trivial-logic guarantee + one small
> empirical demo (n=1 chain).** Independent validation would be a real help, not a formality.

## Use it
**1. Write a fact-set** — the things that must survive. Two ways:
- **Prose / non-coders → `--facts facts.txt`**: one constraint per line — a literal substring (must be
  PRESENT), `re:` for a regex, or `not:` / `not re:` for an **anti-fact** that must be ABSENT (catches a
  negated or forbidden phrase). Example `example/policy.facts.txt` (5 facts):
  ```
  90 days
  PRIV-88
  35 days
  auditor
  re:GDPR Art\.?\s*17
  ```
- **Code-behavior → `--checks checks.py`**: a Python module `CHECKS = [(name, fn(module_or_None, src)->bool)]`
  (lets you assert behavior, e.g. `is_expired({"ttl":0},1e9) is False`). See `example/checks.py`.

You don't have to hand-write the list: give any LLM `extract_facts_prompt.md` + your document to **draft**
`facts.txt`, **review it once**, then validate the draft with `gate.py --facts facts.txt --file <doc>` (every
listed fact should already be present). The gate enforces it forever after; you only curate once.

**2. Gate every rewrite** — pass the **frozen original** as `--baseline` (not the previous pass, or slow drift
sneaks through), and let `--apply` accept-or-revert automatically:
```bash
# your agent rewrote the doc into candidate.md, then:
python gate.py --facts facts.txt --baseline ORIGINAL.md --candidate candidate.md --apply live.md
#   ACCEPT (exit 0) -> live.md is overwritten with candidate
#   REJECT (exit 1) -> live.md is left untouched (the lossy pass is discarded); retry
```
Audit a single file: `python gate.py --facts facts.txt --file doc.md` (exit 1 if any fact missing).

**3. (optional) inject `SKILL.md`** into the editing agent so fewer passes get rejected.

**Where to run the gate** (CI, pre-commit hook, the auto loop, or as an MCP tool an agent can call) →
[`integrations/`](integrations/README.md). The guarantee comes from running it as a step that **can't be
skipped** (CI / hook / loop); MCP & the skill make it *callable*, not guaranteed.

**Automated loop (`guarded_rewrite.py`).** Instead of gating by hand, run the whole edit→gate→accept/revert
loop, with your LLM as a pluggable rewrite command:
```bash
python guarded_rewrite.py --doc live.md --facts facts.txt \
  --rewrite-cmd "your-llm-cli --condense" --passes 8 --retries 1
# each pass: <rewrite-cmd> edits a candidate in place -> gate -> ACCEPT (keep) or REVERT (discard, retry).
# Guarantees: every accepted version still contains every listed fact, over all 8 passes.
```

## Files
`gate.py` (the gate, code + prose) · `guarded_rewrite.py` (the auto loop) · `SKILL.md` (Drift Shield, soft
layer) · `extract_facts_prompt.md` (draft a fact-set with any LLM) · `test_gate.py` (11 unit tests, in CI) ·
`test_gate_fuzz.py` (4 property suites, 800+ randomized cases — the guarantee, fuzzed; in CI) ·
`example/` (code: `doc.py`/`checks.py`/`degraded.py`; prose: `policy.md`/`policy.facts.txt`/`policy_drifted.md`;
`multipass_demo.py` — the offline many-passes gated-vs-ungated demo, in CI).

## Proof (self-test, `example/`)
```
$ gate.py --checks example/checks.py --file example/doc.py
7/7 facts present in example/doc.py                          (exit 0)
$ gate.py --checks example/checks.py --file example/degraded.py
5/7 facts present in example/degraded.py  | MISSING: rationale: SEC-12 present; rationale: INC-2231 present   (exit 1)
$ gate.py --checks example/checks.py --baseline example/doc.py --candidate example/degraded.py
REJECT: candidate dropped 2 fact(s) the baseline had: rationale: SEC-12 present; rationale: INC-2231 present (exit 1)
```
`degraded.py` is a realistic drift: an LLM kept the code but stripped the rationale comments — the *why* is
gone. Behavior tests still pass; the **text checks catch the lost institutional knowledge**.

Prose works the same (`example/policy.md`, a retention policy):
```
$ gate.py --facts example/policy.facts.txt --file example/policy.md
5/5 facts present                                            (exit 0)
$ gate.py --facts example/policy.facts.txt --file example/policy_drifted.md
2/5 facts present in example/policy_drifted.md  | MISSING: 90 days; PRIV-88; re:GDPR Art\.?\s*17   (exit 1)
$ gate.py --facts example/policy.facts.txt --baseline example/policy.md --candidate example/policy_drifted.md --apply live.md
REJECT: candidate dropped 3 fact(s) the baseline had: 90 days; PRIV-88; re:GDPR Art\.?\s*17  | kept previous version (exit 1; live.md untouched)
```
The drifted policy "tightened" 90→60 days and dropped the ticket + the legal "GDPR Art 17" — exactly the
kind of constraint a rewrite silently loses, and the kind no test suite would ever catch.

**Many-passes demo (the literal "edit the same doc repeatedly" case):**
`python example/multipass_demo.py` runs one document through 6 condense passes two ways — **ungated drifts**
(5→2 facts), **gated holds** (5/5, the harmless tidy passes kept, the lossy ones reverted). The rewriter is a
deterministic *simulator*, so this demonstrates the loop/gate **mechanism** over many passes, not a real
model's drift rate (that needs the powered run, `../REPORT.md`).

**The guarantee, fuzzed:** `python test_gate_fuzz.py` checks the gate against an independent oracle over 800+
random documents/fact-sets/rewrites — the decision rule is sound *and* complete, CLI exit codes match, and the
loop **never loses a fact that was present at the start**, no matter the passes (a sabotaged gate is caught).

## Prior art & where this sits

**In plain words:** drift-guard is *not* a new detection algorithm. Checking "this exact phrase must be in the
file" is old (every linter does it). What's new here is the **framing and the packaging**: making
"these listed facts survive every rewrite" an *enforced, executable guarantee*, wrapped in one
zero-dependency file, with an honest line about what a prompt can and can't promise. If you already know these
tools, here's exactly where drift-guard fits — and what it deliberately does *not* try to be:

| Neighbour | What it does | drift-guard's relation |
|---|---|---|
| **Vale** (prose linter) | required/forbidden terms & style rules for docs, in CI | Same "required substring in CI" idea — but single-file/no-config-engine, aimed at *iterative-rewrite drift* and adding the **baseline→candidate regression** mode + the guarded loop. |
| **OPA / Conftest / policy-as-code** | an executable gate that *rejects* configs violating an invariant | Same "a check that runs and rejects = a guarantee" philosophy, applied to **facts in a document** (code *or* prose) and to the rewrite loop. |
| **SummaC · AlignScore · GenAudit · ContractNLI** (semantic frontier) | ML/NLI models that judge *meaning*-preservation / faithfulness | The thing drift-guard **deliberately does NOT do.** A model judge is non-deterministic and DPI-bound — it can only *reduce*, never *guarantee* (same status as the skill). Keeping the gate dumb-but-deterministic is the whole point. |

**The contribution is therefore the DPI framing + a zero-dep single-file artifact + honest scope (including
negative results on the skill)** — not a novel detection method. We don't claim to beat the semantic tools;
we claim a different, deterministic guarantee they can't make.

## When this matters (honest scope)
- **Strong fit:** many-pass iterative pipelines; **prose/specs/contracts/knowledge-bases with no test suite**
  (there's no CI to catch lost constraints); rationale/"why" that tests never cover.
- **Weak fit:** ordinary code already protected by tests + review run every change — there the gate ≈ "run
  your tests", and its only extra value is guarding *untested* invariants and *rationale comments*.

## Notes
Pure stdlib. The gate is the contribution; the skill is convenience. A `checks.py` is to a document what a
test suite is to code — drift-guard is "CI for the facts in a file." See `../DRIFT.md` for why the math says
the gate (not the prompt) is what gives a guarantee.
