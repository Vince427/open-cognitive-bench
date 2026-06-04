"""guarded_rewrite: drive an LLM rewrite loop with the fact-gate enforcing zero drift.

Each pass: produce a candidate rewrite -> gate it against the FROZEN fact-set -> ACCEPT (keep) or REVERT
(discard the lossy pass, retry). So every accepted version still contains every listed fact, no matter how
many passes run. The rewrite step is pluggable: a shell command (your LLM CLI) on the CLI, or a Python
callable in `run()` (used by the tests).

CLI:
  python guarded_rewrite.py --doc D --facts F --rewrite-cmd "your-llm-cli --in" --passes 8 --retries 1
    The command is invoked as:  <rewrite-cmd> <candidate_path>   and must edit <candidate_path> in place.
"""
from __future__ import annotations
import argparse
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate  # noqa: E402


def missing_facts(text, checks, suffix=".txt"):
    """Which listed facts are absent from `text` (written to a temp file so code-behavior checks can import)."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / ("doc" + suffix)
        p.write_text(text, encoding="utf-8")
        res = gate.run(p, checks)
    return [n for n, _ in checks if not res[n]]


def run(doc_path, checks, rewrite, passes=5, retries=1, log=print):
    """rewrite: (current_text)->candidate_text. Gate enforces the fact-set; lossy passes are reverted."""
    doc = Path(doc_path)
    suffix = doc.suffix or ".txt"
    accepted = kept = 0
    for p in range(1, passes + 1):
        ok = False
        for attempt in range(retries + 1):
            cand = rewrite(doc.read_text(encoding="utf-8"))
            miss = missing_facts(cand, checks, suffix)
            if not miss:
                doc.write_text(cand, encoding="utf-8")
                accepted += 1
                ok = True
                log(f"pass {p}: ACCEPT")
                break
            log(f"pass {p} attempt {attempt + 1}: REJECT (would drop: {', '.join(miss)})")
        if not ok:
            kept += 1
            log(f"pass {p}: kept previous version (all {retries + 1} attempts dropped a fact)")
    final = missing_facts(doc.read_text(encoding="utf-8"), checks, suffix)
    log(f"done: {accepted} accepted, {kept} reverted; facts intact = {not final}"
        + ("" if not final else f"  | STILL MISSING (were already gone at start?): {final}"))
    return {"accepted": accepted, "reverted": kept, "final_missing": final}


def _cmd_rewriter(cmd, suffix):
    def rewrite(text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ("cand" + suffix)
            p.write_text(text, encoding="utf-8")
            subprocess.run(shlex.split(cmd) + [str(p)], check=False)
            return p.read_text(encoding="utf-8")
    return rewrite


def main():
    ap = argparse.ArgumentParser(description="guarded LLM rewrite loop (fact-gated)")
    ap.add_argument("--doc", required=True)
    ap.add_argument("--facts")
    ap.add_argument("--checks")
    ap.add_argument("--rewrite-cmd", required=True, help="invoked as: <cmd> <candidate_path>; edits it in place")
    ap.add_argument("--passes", type=int, default=5)
    ap.add_argument("--retries", type=int, default=1)
    args = ap.parse_args()
    if bool(args.checks) == bool(args.facts):
        ap.error("give exactly one of --checks or --facts")
    checks = gate.load_checks_py(args.checks) if args.checks else gate.load_facts_txt(args.facts)
    suffix = Path(args.doc).suffix or ".txt"
    res = run(args.doc, checks, _cmd_rewriter(args.rewrite_cmd, suffix), args.passes, args.retries)
    sys.exit(0 if not res["final_missing"] else 1)


if __name__ == "__main__":
    main()
