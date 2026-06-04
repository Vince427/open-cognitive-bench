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

## Use it
1. Write a **fact-set** for your document — a `checks.py` exposing `CHECKS = [(name, fn)]`, where
   `fn(module_or_None, source_text) -> bool`. Mix *behavior* checks (need the module) and *text/rationale*
   checks (substring/regex on the source — these are what drift kills first). See `example/checks.py`.
2. Wrap each LLM edit in the gate (the loop primitive):
   ```bash
   # agent rewrites doc.py -> candidate.py, then:
   python gate.py --checks checks.py --baseline doc.py --candidate candidate.py \
     && mv candidate.py doc.py          # ACCEPT (exit 0): keep it
     || echo "REJECT: kept the previous version; retry the pass"   # exit 1: a fact was lost
   ```
   Or just audit one file: `python gate.py --checks checks.py --file doc.py` (exit 1 if any fact missing).
3. Optionally inject `SKILL.md` into the editing agent so fewer passes get rejected.

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

## When this matters (honest scope)
- **Strong fit:** many-pass iterative pipelines; **prose/specs/contracts/knowledge-bases with no test suite**
  (there's no CI to catch lost constraints); rationale/"why" that tests never cover.
- **Weak fit:** ordinary code already protected by tests + review run every change — there the gate ≈ "run
  your tests", and its only extra value is guarding *untested* invariants and *rationale comments*.

## Notes
Pure stdlib. The gate is the contribution; the skill is convenience. A `checks.py` is to a document what a
test suite is to code — drift-guard is "CI for the facts in a file." See `../DRIFT.md` for why the math says
the gate (not the prompt) is what gives a guarantee.
