"""Property-based / fuzz tests for the drift-guard fact-gate. Pure stdlib, deterministic (seeded).

Why this exists: `test_gate.py` proves the gate on ~10 hand-picked cases. The gate's *headline* claim is a
GUARANTEE ("every fact you list survives every rewrite"), and a guarantee deserves more than ten examples.
Here we generate hundreds of random documents, fact-sets, and (often lossy) rewrites and check the gate
against an INDEPENDENT oracle:

  P1  regression-gate soundness+completeness: the gate ACCEPTs a candidate IFF it keeps every fact the
      baseline had — for every random (baseline, candidate, fact-set). Catches any bug in the decision rule,
      not just the substring check (the oracle re-derives membership separately from gate.run's file/module path).
  P2  the GUARANTEE (loop invariant): drive guarded_rewrite with an arbitrary, adversarial, possibly-lossy
      rewriter for many passes/retries; assert no fact present at the start is ever missing at the end.
      This is the literal "won't lose info over repeated edits" promise, fuzzed.
  P3  CLI exit codes match the decision on random cases (0 = ACCEPT/all-present, 1 = REJECT/missing).
  P4  code-behavior facts (`--checks`): a numeric-boundary check rejects exactly the candidates that break it.

Run directly (exits non-zero on any failure) or under pytest:
    python drift-guard/test_gate_fuzz.py
"""
from __future__ import annotations
import random
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate            # noqa: E402
import guarded_rewrite  # noqa: E402


# ---- independent oracle (the spec, re-implemented separately from gate.run) -------------------------
def present(text, raw):
    """Is fact `raw` present in `text`? Mirrors the SPEC, not gate's implementation path."""
    if raw.startswith("re:"):
        return re.search(raw[3:], text) is not None
    return raw in text


# ---- random fact-sets and documents -----------------------------------------------------------------
def make_facts(rng):
    """A unique, collision-free fact-set: literal substrings + a few 're:' regexes. Each token appears
    nowhere else by construction, so dropping its line truly removes the fact."""
    facts = []
    for i in range(rng.randint(2, 6)):
        tok = f"FACT_{i}_{rng.randrange(16**6):06x}"          # literal, globally unique
        facts.append((tok, tok))                             # (line-in-doc, fact-string)
    for i in range(rng.randint(1, 3)):
        n = rng.randrange(10, 9999)
        facts.append((f"CODE_{i}_{n}", rf"re:CODE_{i}_\d+"))  # regex, matched by the line we plant
    rng.shuffle(facts)
    return facts


def make_doc(rng, facts):
    """Build a document: each fact on its own line, interspersed with filler from a DISJOINT alphabet
    (lower-case words) that can never accidentally contain a fact token (which are upper-case/underscore)."""
    lines = [line for line, _ in facts]
    filler = [" ".join(rng.choice(["lorem", "ipsum", "dolor", "sit", "amet", "the", "why"])
                        for _ in range(rng.randint(1, 5)))
              for _ in range(rng.randint(0, 8))]
    body = lines + filler
    rng.shuffle(body)
    return "\n".join(body) + "\n"


def mutate(rng, doc):
    """A random rewrite: drop each line with some probability, add disjoint filler, reorder."""
    kept = [ln for ln in doc.splitlines() if rng.random() > rng.choice([0.1, 0.3, 0.5])]
    kept += [" ".join(rng.choice(["tidy", "rephrase", "summary", "note"]) for _ in range(rng.randint(1, 4)))
             for _ in range(rng.randint(0, 3))]
    rng.shuffle(kept)
    return "\n".join(kept) + "\n"


def _facts_file(d, facts):
    p = Path(d) / "facts.txt"
    p.write_text("\n".join(fact for _, fact in facts) + "\n", encoding="utf-8")
    return gate.load_facts_txt(p)


def _gate_regressions(d, baseline_text, candidate_text, checks):
    """Run the gate's regression logic via gate.run on real temp files (its production path)."""
    b = Path(d) / "baseline.txt"; b.write_text(baseline_text, encoding="utf-8")
    c = Path(d) / "candidate.txt"; c.write_text(candidate_text, encoding="utf-8")
    rb, rc = gate.run(b, checks), gate.run(c, checks)
    names = [n for n, _ in checks]
    return [n for n in names if rb[n] and not rc[n]]


# ---- P1: regression-gate soundness + completeness ---------------------------------------------------
def test_fuzz_regression_matches_oracle():
    rng = random.Random(1234)
    for _ in range(400):
        facts = make_facts(rng)
        doc = make_doc(rng, facts)
        cand = mutate(rng, doc)
        with tempfile.TemporaryDirectory() as d:
            checks = _facts_file(d, facts)
            gate_reg = set(_gate_regressions(d, doc, cand, checks))
        # independent oracle: a regression = a fact present in baseline but absent from candidate
        oracle_reg = {fact for _, fact in facts if present(doc, fact) and not present(cand, fact)}
        assert gate_reg == oracle_reg, (gate_reg, oracle_reg)
        # ACCEPT (no regressions) IFF every baseline-present fact survives in the candidate
        accept = not gate_reg
        all_survive = all(present(cand, fact) for _, fact in facts if present(doc, fact))
        assert accept == all_survive


# ---- P2: THE GUARANTEE — no present fact is ever lost across many adversarial passes ----------------
def test_fuzz_loop_never_loses_a_fact():
    rng = random.Random(99)
    for _ in range(200):
        facts = make_facts(rng)
        doc_text = make_doc(rng, facts)
        with tempfile.TemporaryDirectory() as d:
            checks = _facts_file(d, facts)
            doc = Path(d) / "live.txt"; doc.write_text(doc_text, encoding="utf-8")
            start_present = [fact for _, fact in facts if present(doc_text, fact)]

            # an arbitrary, often-lossy rewriter: randomly drops lines (sometimes a fact line) + tidies
            def adversary(text, _rng=rng):
                out = [ln for ln in text.splitlines() if _rng.random() > 0.4]
                if _rng.random() < 0.5:
                    out.append("tidied")
                return "\n".join(out) + "\n"

            guarded_rewrite.run(doc, checks, adversary,
                                passes=rng.randint(1, 6), retries=rng.randint(0, 2), log=lambda *a: None)
            final = doc.read_text(encoding="utf-8")
        # the promise: everything present at the start is still present at the end, no matter the passes
        for fact in start_present:
            assert present(final, fact), f"GUARANTEE VIOLATED: lost {fact!r}"


# ---- P3: CLI exit codes match the decision ----------------------------------------------------------
def _cli(*args):
    import contextlib, io
    old = sys.argv
    sys.argv = ["gate.py", *args]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            gate.main()
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else (0 if not e.code else 1)
    finally:
        sys.argv = old


def test_fuzz_cli_exit_codes():
    rng = random.Random(7)
    for _ in range(120):
        facts = make_facts(rng)
        doc = make_doc(rng, facts)
        cand = mutate(rng, doc)
        with tempfile.TemporaryDirectory() as d:
            ff = Path(d) / "facts.txt"
            ff.write_text("\n".join(fact for _, fact in facts) + "\n", encoding="utf-8")
            cf = Path(d) / "cand.txt"; cf.write_text(cand, encoding="utf-8")
            df = Path(d) / "doc.txt"; df.write_text(doc, encoding="utf-8")
            # file mode: exit 1 iff a fact is missing from the candidate
            expect_file = 1 if any(not present(cand, fact) for _, fact in facts) else 0
            assert _cli("--facts", str(ff), "--file", str(cf)) == expect_file
            # regression mode: exit 1 iff the candidate drops a fact the (all-present) doc had
            expect_reg = 1 if any(present(doc, fact) and not present(cand, fact) for _, fact in facts) else 0
            assert _cli("--facts", str(ff), "--baseline", str(df), "--candidate", str(cf)) == expect_reg


# ---- P4: code-behavior facts (--checks) catch a broken numeric boundary -----------------------------
def test_fuzz_code_behavior_boundary():
    # fact: is_expired(ttl, now) must treat now == ttl as NOT expired (a strict-vs-inclusive boundary bug).
    CHECKS = [("boundary: now==ttl is not expired",
               lambda mod, src: mod is not None and hasattr(mod, "is_expired")
               and mod.is_expired(100, 100) is False and mod.is_expired(100, 101) is True)]
    rng = random.Random(2024)
    for _ in range(80):
        ttl = rng.randrange(1, 10_000)
        good = f"def is_expired(ttl, now):\n    return now > ttl\n"      # correct: strict
        bad = f"def is_expired(ttl, now):\n    return now >= ttl\n"      # off-by-one at the boundary
        with tempfile.TemporaryDirectory() as d:
            gp = Path(d) / "good.py"; gp.write_text(good, encoding="utf-8")
            bp = Path(d) / "bad.py"; bp.write_text(bad, encoding="utf-8")
            assert gate.run(gp, CHECKS)[CHECKS[0][0]] is True
            assert gate.run(bp, CHECKS)[CHECKS[0][0]] is False
            # regression: good -> bad must REJECT (a behavioral fact was dropped)
            assert _cli("--checks", _write_checks(d), "--baseline", str(gp), "--candidate", str(bp)) == 1
            assert _cli("--checks", _write_checks(d), "--baseline", str(gp), "--candidate", str(gp)) == 0
        _ = ttl  # vary the loop without affecting the (boundary-fixed) assertion


def _write_checks(d):
    p = Path(d) / "checks.py"
    p.write_text(
        "CHECKS = [('boundary: now==ttl is not expired',\n"
        "          lambda mod, src: mod is not None and hasattr(mod, 'is_expired')\n"
        "          and mod.is_expired(100, 100) is False and mod.is_expired(100, 101) is True)]\n",
        encoding="utf-8")
    return str(p)


if __name__ == "__main__":
    g = dict(globals())
    tests = sorted((k, v) for k, v in g.items() if k.startswith("test_") and callable(v))
    failed = []
    for name, fn in tests:
        try:
            fn(); print(f"  PASS {name}")
        except Exception as e:  # noqa: BLE001
            failed.append(name); print(f"  FAIL {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - len(failed)}/{len(tests)} property suites passed "
          f"(800+ randomized cases)")
    sys.exit(1 if failed else 0)
