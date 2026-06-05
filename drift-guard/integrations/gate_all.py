"""Gate every protected (file -> fact-set) pair listed in a `.driftguard.json` config; exit 1 if any
load-bearing fact was dropped. This is the shared engine behind the **non-bypassable** deployments
(the pre-commit hook and the CI workflow): the gate runs as a step that *rejects*, not as a tool an agent
may choose to call. Pure stdlib.

Config (`.driftguard.json`):
    {
      "protect": [
        { "file": "docs/policy.md", "facts":  "docs/policy.facts.txt" },
        { "file": "src/cache.py",   "checks": "tests/cache.checks.py" }
      ]
    }
Each entry needs exactly one of "facts" (a declarative list) or "checks" (a Python CHECKS module).

Usage:  python drift-guard/integrations/gate_all.py [path/to/.driftguard.json]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # drift-guard/ -> gate.py
import gate  # noqa: E402


def main(argv):
    cfg_path = Path(argv[0]) if argv else Path(".driftguard.json")
    if not cfg_path.exists():
        print(f"drift-guard: no config at {cfg_path} — nothing to check.")
        return 0
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    items = cfg.get("protect", [])
    failed = 0
    for item in items:
        f = item.get("file")
        if not f:
            print("  SKIP  entry without a \"file\""); failed += 1; continue
        if ("facts" in item) == ("checks" in item):
            print(f"  SKIP  {f}: give exactly one of \"facts\" or \"checks\""); failed += 1; continue
        try:
            checks = gate.load_facts_txt(item["facts"]) if "facts" in item else gate.load_checks_py(item["checks"])
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {f}: cannot load fact-set ({type(e).__name__}: {e})"); failed += 1; continue
        if not Path(f).exists():
            print(f"  FAIL  {f}: file is missing"); failed += 1; continue
        res = gate.run(f, checks)
        lost = [n for n, _ in checks if not res[n]]
        if lost:
            print(f"  FAIL  {f}  | dropped: {'; '.join(lost)}"); failed += 1
        else:
            print(f"  ok    {f}  ({len(checks)} facts present)")
    if failed:
        print(f"\ndrift-guard: {failed}/{len(items)} protected file(s) lost a fact — REJECTED (exit 1).")
        return 1
    print(f"\ndrift-guard: all {len(items)} protected file(s) keep every listed fact (exit 0).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
