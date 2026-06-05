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
   For semantic-critical invariants use the **`--checks`** path instead (a `checks.py` module that asserts
   behavior, e.g. `is_expired(...) is False`, which a negation cannot satisfy).
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
- **Prose / non-coders → `--facts facts.txt`**: one required fact per line (a literal substring, or `re:` for
  a regex). Example `example/policy.facts.txt`:
  ```
  90 days
  PRIV-88
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
layer) · `extract_facts_prompt.md` (draft a fact-set with any LLM) · `test_gate.py` (10 tests, in CI) ·
`example/` (code: `doc.py`/`checks.py`/`degraded.py`; prose: `policy.md`/`policy.facts.txt`/`policy_drifted.md`).

## Proof (self-test, `example/`)
```
$ gate.py --checks example/checks.py --file example/doc.py
7/7 facts present in example/doc.py                          (exit 0)
$ gate.py --checks example/checks.py --file example/degraded.py
5/7 facts present | MISSING: rationale: SEC-12; rationale: INC-2231   (exit 1)
$ gate.py --checks example/checks.py --baseline example/doc.py --candidate example/degraded.py
REJECT: candidate dropped 2 fact(s) the baseline had: SEC-12; INC-2231 (exit 1)
```
`degraded.py` is a realistic drift: an LLM kept the code but stripped the rationale comments — the *why* is
gone. Behavior tests still pass; the **text checks catch the lost institutional knowledge**.

Prose works the same (`example/policy.md`, a retention policy):
```
$ gate.py --facts example/policy.facts.txt --file example/policy.md
5/5 facts present                                            (exit 0)
$ gate.py --facts example/policy.facts.txt --file example/policy_drifted.md
2/5 facts present | MISSING: 90 days; PRIV-88; GDPR Art 17    (exit 1)
$ gate.py --facts ... --baseline policy.md --candidate policy_drifted.md --apply live.md
REJECT: dropped 3 facts | kept previous version              (exit 1; live.md untouched)
```
The drifted policy "tightened" 90→60 days and dropped the ticket + the legal "GDPR Art 17" — exactly the
kind of constraint a rewrite silently loses, and the kind no test suite would ever catch.

## When this matters (honest scope)
- **Strong fit:** many-pass iterative pipelines; **prose/specs/contracts/knowledge-bases with no test suite**
  (there's no CI to catch lost constraints); rationale/"why" that tests never cover.
- **Weak fit:** ordinary code already protected by tests + review run every change — there the gate ≈ "run
  your tests", and its only extra value is guarding *untested* invariants and *rationale comments*.

## Notes
Pure stdlib. The gate is the contribution; the skill is convenience. A `checks.py` is to a document what a
test suite is to code — drift-guard is "CI for the facts in a file." See `../DRIFT.md` for why the math says
the gate (not the prompt) is what gives a guarantee.
