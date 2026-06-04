"""drift-guard: an executable fact-gate against iterative-rewrite drift.

The GATE is the substance (a prompt/skill only *slows* drift; see ../DRIFT.md, Data-Processing-Inequality).
Run it after every LLM pass; it REJECTS a pass that drops a load-bearing fact, so "all facts preserved" is an
invariant of the rewrite loop. Pure stdlib; works for code (.py) and for prose.

Define the fact-set EITHER as:
  --checks checks.py   a Python module exposing CHECKS = [(name, fn(module_or_None, source_text)->bool)]
                       (use for code-behavior facts; the doc module is imported and passed in).
  --facts facts.txt    a plain declarative list (use for prose / non-coders), one required fact per line:
                         100 requests/minute        # literal substring that must be present
                         re:\\bMAX_RPM\\s*=\\s*100\\b  # a regex (prefix 're:')
                       blank lines and lines starting with '#' are ignored.

Modes:
  gate.py --facts F --file doc.md                         audit one file; exit 1 if any fact missing.
  gate.py --facts F --baseline ORIG --candidate NEW       regression gate: exit 1 (REJECT) iff NEW drops a
                                                          fact ORIG had. Pass the FROZEN ORIGINAL as baseline
                                                          (not the previous pass) to stop slow cumulative drift.
  ... add --apply OUT                                     on ACCEPT, write NEW to OUT (keep it); on REJECT,
                                                          leave OUT untouched (revert). The guarded-rewrite loop.
"""
from __future__ import annotations
import argparse
import importlib.util as u
import re
import shutil
import sys
from pathlib import Path


def load_checks_py(path):
    spec = u.spec_from_file_location("dg_checks", path)
    m = u.module_from_spec(spec)
    spec.loader.exec_module(m)
    return list(m.CHECKS)


def load_facts_txt(path):
    """Build CHECKS from a declarative fact list (literal substrings, or 're:' regexes)."""
    checks = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            pat = re.compile(line[3:])
            checks.append((line, (lambda p: (lambda mod, src: p.search(src) is not None))(pat)))
        else:
            needle = line
            checks.append((line, (lambda n: (lambda mod, src: n in src))(needle)))
    return checks


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
    ap.add_argument("--checks", help="Python fact-set module (CHECKS=[(name,fn)])")
    ap.add_argument("--facts", help="declarative fact list (substrings / 're:' regexes)")
    ap.add_argument("--file")
    ap.add_argument("--baseline", help="the FROZEN ORIGINAL to gate against")
    ap.add_argument("--candidate")
    ap.add_argument("--apply", dest="apply_to", help="on ACCEPT, write candidate here (revert = leave it)")
    args = ap.parse_args()

    if bool(args.checks) == bool(args.facts):
        ap.error("give exactly one of --checks or --facts")
    checks = load_checks_py(args.checks) if args.checks else load_facts_txt(args.facts)
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
            print(f"REJECT: candidate dropped {len(regressions)} fact(s) the baseline had: " + "; ".join(regressions)
                  + ("  | kept previous version" if args.apply_to else ""))
            sys.exit(1)
        if args.apply_to:
            shutil.copyfile(args.candidate, args.apply_to)
        print(f"ACCEPT: candidate preserves all {sum(b.values())} facts the baseline had."
              + (f"  | wrote {args.apply_to}" if args.apply_to else ""))
        sys.exit(0)

    ap.error("use --file, or --baseline with --candidate")


if __name__ == "__main__":
    main()
