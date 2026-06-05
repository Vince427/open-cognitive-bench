"""Offline, reproducible multi-pass drift demo — the literal "edit the same document many times" scenario.

It runs ONE document through several "condense" passes two ways and prints the contrast:
  - UNGATED  : passes applied directly        -> facts decay toward zero (silent "broken telephone" drift).
  - GATED    : the same passes via the fact-gate -> every listed fact survives all passes (the guarantee),
               while the harmless tidy-edits are still kept.

HONEST SCOPE: the "rewriter" here is a DETERMINISTIC SIMULATOR, not a real LLM — every even pass deliberately
trims a load-bearing line ("this looks redundant"), every odd pass makes a harmless cosmetic edit. So this
demonstrates the LOOP + GATE *mechanism* over many passes (and proves the gate code holds the invariant); it
does NOT measure how fast a real model drifts — that needs the powered API run (see ../../REPORT.md). The math
for "why an unchecked rewrite chain can only lose information" is the Data-Processing-Inequality (../../DRIFT.md).

Run:  python drift-guard/example/multipass_demo.py        (exits 1 if the gated guarantee is ever violated)
"""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DG = HERE.parent
sys.path.insert(0, str(DG))
import gate            # noqa: E402
import guarded_rewrite  # noqa: E402

# Five load-bearing facts (unique literal substrings, each on its own line in SEED, no collisions).
FACTS = [
    ("retention window", "90 days"),
    ("internal ticket", "PRIV-88"),
    ("legal basis", "GDPR Art. 17"),
    ("rate limit", "100 requests/minute"),
    ("owner", "owner: data-platform"),
]

SEED = """# Data Retention Policy (v3)

Personal data is retained for 90 days, then purged.
This window was set under PRIV-88 after the 2023 incident review.
Erasure-on-request is honored within the window per GDPR Art. 17.
The export endpoint is capped at 100 requests/minute to protect the purge job.
This policy is owned by owner: data-platform; changes require their sign-off.

Rationale: shorter windows reduce blast radius; the cap stops backfills starving the purge.
"""


def facts_present(text):
    """The subset of listed facts still present in `text` (literal substring membership)."""
    return [tok for _, tok in FACTS if tok in text]


def make_condenser():
    """A deterministic 'condense' rewriter with its own pass counter (one call == one pass at retries=0):
    even pass -> trim the first line that still carries a fact ('looks redundant'); odd pass -> cosmetic tidy.
    Both always append a visible marker so accepted edits are observable."""
    tokens = [tok for _, tok in FACTS]
    state = {"n": 0}

    def rewrite(text):
        state["n"] += 1
        n = state["n"]
        lines = text.splitlines()
        if n % 2 == 0:  # the lossy move: drop the first still-present fact-bearing line
            for i, ln in enumerate(lines):
                if any(tok in ln for tok in tokens):
                    del lines[i]
                    break
        lines.append(f"<!-- condensed: pass {n} -->")
        return "\n".join(lines) + "\n"

    return rewrite


def run_ungated(passes=6):
    """Apply the condenser directly, no gate. Returns per-pass records and the final surviving facts."""
    text = SEED
    records = [("start", facts_present(text), None)]
    condense = make_condenser()
    for p in range(1, passes + 1):
        before = set(facts_present(text))
        text = condense(text)
        after = facts_present(text)
        lost = sorted(before - set(after))
        records.append((f"pass {p}", after, lost[0] if lost else None))
    return records, facts_present(text)


def run_gated(passes=6):
    """Drive the SAME condenser through guarded_rewrite (the real loop). Returns its log + surviving facts."""
    with tempfile.TemporaryDirectory() as d:
        ff = Path(d) / "facts.txt"
        ff.write_text("\n".join(tok for _, tok in FACTS) + "\n", encoding="utf-8")
        checks = gate.load_facts_txt(ff)
        doc = Path(d) / "live.md"
        doc.write_text(SEED, encoding="utf-8")
        logs = []
        guarded_rewrite.run(doc, checks, make_condenser(), passes=passes, retries=0, log=logs.append)
        return logs, facts_present(doc.read_text(encoding="utf-8"))


def main():
    n = len(FACTS)
    passes = 6
    print(f"Document: {n} load-bearing facts; {passes} 'condense' passes (even passes trim, odd passes tidy).\n")

    print("UNGATED (passes applied directly — no checking):")
    ung_records, ung_final = run_ungated(passes)
    for label, present, lost in ung_records:
        note = f"   <- dropped {lost!r}" if lost else ""
        print(f"  {label:<8} {len(present)}/{n} facts{note}")
    print(f"  RESULT: {len(ung_final)}/{n} facts survived — silent drift.\n")

    print("GATED (same passes, through the fact-gate):")
    gat_logs, gat_final = run_gated(passes)
    for line in gat_logs:
        print(f"  {line}")
    print(f"  RESULT: {len(gat_final)}/{n} facts survived — guarantee held "
          f"(the harmless tidy passes were kept; the lossy ones were reverted).\n")

    print("Honest scope: the rewriter is a deterministic SIMULATOR, not a real LLM — this proves the gate/loop "
          "mechanism over many passes, not a model's drift rate. See ../../DRIFT.md (the DPI math) and "
          "../../REPORT.md (the powered run still owed).")

    # Living check: ungated MUST lose ≥1 fact; gated MUST keep all.
    if len(ung_final) >= n:
        print("\nUNEXPECTED: ungated chain did not drift; demo invariant broken.", file=sys.stderr)
        return 1
    if len(gat_final) != n:
        print(f"\nGUARANTEE VIOLATED: gated chain lost facts ({len(gat_final)}/{n}).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
