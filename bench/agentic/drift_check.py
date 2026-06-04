"""Verify the 5 load-bearing facts survive in a (possibly edited) version of drift_seed.py.
Usage: python bench/agentic/drift_check.py <path-to-module.py>  ->  prints "k/5" + which were lost."""
import importlib.util as u
import sys
from pathlib import Path

CHECKS = []  # (name, fn(mod, src) -> bool)
CHECKS.append(("MAX_RPM==100 + SEC-12 rationale",
               lambda m, s: getattr(m, "MAX_RPM", None) == 100 and "SEC-12" in s))
CHECKS.append(("ttl==0 never expires (sentinel)",
               lambda m, s: m.is_expired({"ttl": 0, "created": 0}, 10 ** 9) is False))
CHECKS.append(("render_comment escapes XSS",
               lambda m, s: "<script>" not in m.render_comment("<script>") and "&lt;script&gt;" in m.render_comment("<script>")))
CHECKS.append(("join_lines uses sep='\\n' (public API)",
               lambda m, s: m.join_lines(["a", "b"]) == "a\nb"))
CHECKS.append(("recent preserves first-seen order",
               lambda m, s: m.recent([3, 1, 2, 1, 3]) == [3, 1, 2]))


def check(path):
    src = Path(path).read_text(encoding="utf-8")
    for k in ("driftmod",):
        sys.modules.pop(k, None)
    spec = u.spec_from_file_location("driftmod", path)
    lost = []
    try:
        mod = u.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:  # whole file broke -> all facts lost
        return 0, [f"{n} <module error: {type(e).__name__}>" for n, _ in CHECKS]
    survived = 0
    for name, fn in CHECKS:
        try:
            ok = bool(fn(mod, src))
        except Exception:
            ok = False
        survived += ok
        if not ok:
            lost.append(name)
    return survived, lost


if __name__ == "__main__":
    s, lost = check(sys.argv[1])
    print(f"{s}/{len(CHECKS)} facts survived" + ("" if not lost else "  | LOST: " + "; ".join(lost)))
