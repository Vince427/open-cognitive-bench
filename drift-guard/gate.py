"""drift-guard: an executable fact-gate against iterative-rewrite drift.

The GATE is the substance (a prompt/skill only *slows* drift; see ../DRIFT.md, Data-Processing-Inequality).
Run it after every LLM pass; it REJECTS a pass that drops a load-bearing fact, so "all facts preserved" is an
invariant of the rewrite loop. Pure stdlib; works for code (.py) and prose (text predicates).

A `checks` module defines `CHECKS = [(name, fn)]`, where fn(module_or_None, source_text) -> bool.
For .py docs the module is imported and passed; for prose, module is None and fn inspects source_text.

Modes:
  python gate.py --checks checks.py --file doc.py
      report which facts survive in doc.py; exit 1 if any are missing.
  python gate.py --checks checks.py --baseline old.py --candidate new.py
      REGRESSION gate: exit 1 (REJECT) iff new.py loses a fact that old.py had. This is the loop primitive:
      reject -> keep old.py, retry the pass.
"""
from __future__ import annotations
import argparse
import importlib.util as u
import sys
from pathlib import Path


def load_checks(path):
    spec = u.spec_from_file_location("dg_checks", path)
    m = u.module_from_spec(spec)
    spec.loader.exec_module(m)
    return list(m.CHECKS)


def load_module(path):
    if not str(path).endswith(".py"):
        return None
    try:
        spec = u.spec_from_file_location("dg_doc", path)
        m = u.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except Exception:
        return None  # a broken module = every code-fact is "lost"


def run(path, checks):
    src = Path(path).read_text(encoding="utf-8")
    mod = load_module(path)
    res = {}
    for name, fn in checks:
        try:
            res[name] = bool(fn(mod, src))
        except Exception:
            res[name] = False
    return res


def main():
    ap = argparse.ArgumentParser(description="drift-guard fact-gate")
    ap.add_argument("--checks", required=True)
    ap.add_argument("--file")
    ap.add_argument("--baseline")
    ap.add_argument("--candidate")
    args = ap.parse_args()
    checks = load_checks(args.checks)
    names = [n for n, _ in checks]

    if args.file:
        res = run(args.file, checks)
        lost = [n for n in names if not res[n]]
        print(f"{len(names) - len(lost)}/{len(names)} facts present in {args.file}"
              + ("" if not lost else "  | MISSING: " + "; ".join(lost)))
        sys.exit(0 if not lost else 1)

    if args.baseline and args.candidate:
        b, c = run(args.baseline, checks), run(args.candidate, checks)
        regressions = [n for n in names if b[n] and not c[n]]
        if regressions:
            print(f"REJECT: candidate dropped {len(regressions)} fact(s) the baseline had: " + "; ".join(regressions))
            sys.exit(1)
        print(f"ACCEPT: candidate preserves all {sum(b.values())} facts the baseline had.")
        sys.exit(0)

    ap.error("use --file, or --baseline with --candidate")


if __name__ == "__main__":
    main()
