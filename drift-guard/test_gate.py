"""Tests for the drift-guard fact-gate. Pure stdlib; runs under pytest or directly:
    python drift-guard/test_gate.py   (exits non-zero on any failure)
Covers the fact-set parsers, the per-file fact check, the regression decision, and the CLI exit codes."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate  # noqa: E402

EX = HERE / "example"
FACTS = EX / "policy.facts.txt"


# ---- fact-set parsing -------------------------------------------------------------------------------
def test_facts_txt_parses_literal_and_regex():
    checks = gate.load_facts_txt(FACTS)
    names = [n for n, _ in checks]
    assert "90 days" in names and any(n.startswith("re:") for n in names)
    assert "# comment" not in "".join(names)  # comments/blanks dropped


def test_checks_py_loads():
    checks = gate.load_checks_py(EX / "checks.py")
    assert len(checks) >= 5 and all(callable(fn) for _, fn in checks)


# ---- per-file fact presence -------------------------------------------------------------------------
def _missing(path, checks):
    res = gate.run(path, checks)
    return [n for n, _ in checks if not res[n]]


def test_prose_original_all_present():
    assert _missing(EX / "policy.md", gate.load_facts_txt(FACTS)) == []


def test_prose_drifted_loses_facts():
    miss = _missing(EX / "policy_drifted.md", gate.load_facts_txt(FACTS))
    assert "90 days" in miss and "PRIV-88" in miss and any(m.startswith("re:") for m in miss)


def test_code_behavior_facts():
    checks = gate.load_checks_py(EX / "checks.py")
    assert _missing(EX / "doc.py", checks) == []           # healthy
    assert _missing(EX / "degraded.py", checks)            # drifted loses ≥1


def test_broken_module_loses_all_code_facts():
    checks = gate.load_checks_py(EX / "checks.py")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "broken.py"
        p.write_text("def is_expired(:\n  pass\n", encoding="utf-8")  # syntax error
        # every behavior check should fail (module won't import); count missing > 0
        assert len(_missing(p, checks)) >= 1


# ---- CLI exit codes (the loop primitive) -- run in-process (portable; no subprocess) ----------------
def _cli(*args):
    import contextlib
    import io
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


def test_cli_file_mode_exit_codes():
    assert _cli("--facts", str(FACTS), "--file", str(EX / "policy.md")) == 0
    assert _cli("--facts", str(FACTS), "--file", str(EX / "policy_drifted.md")) == 1


def test_cli_regression_and_apply():
    assert _cli("--facts", str(FACTS), "--baseline", str(EX / "policy.md"),
                "--candidate", str(EX / "policy.md")) == 0
    assert _cli("--facts", str(FACTS), "--baseline", str(EX / "policy.md"),
                "--candidate", str(EX / "policy_drifted.md")) == 1
    with tempfile.TemporaryDirectory() as d:
        live = Path(d) / "live.md"
        live.write_text((EX / "policy.md").read_text(encoding="utf-8"), encoding="utf-8")
        # reject must NOT overwrite live
        _cli("--facts", str(FACTS), "--baseline", str(EX / "policy.md"),
             "--candidate", str(EX / "policy_drifted.md"), "--apply", str(live))
        assert "PRIV-88" in live.read_text(encoding="utf-8")


# ---- guarded_rewrite driver (in-process fake rewriters) ---------------------------------------------
import guarded_rewrite  # noqa: E402


def _tmp_copy(src):
    d = tempfile.mkdtemp()
    p = Path(d) / src.name
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return p


def test_driver_reverts_a_lossy_pass():
    doc = _tmp_copy(EX / "policy.md")
    checks = gate.load_facts_txt(FACTS)
    drop = lambda text: text.replace("PRIV-88", "REDACTED")  # noqa: E731  (a lossy rewrite)
    res = guarded_rewrite.run(doc, checks, drop, passes=3, retries=0, log=lambda *a: None)
    assert res["accepted"] == 0 and res["reverted"] == 3
    assert res["final_missing"] == []                  # reverts kept the doc intact
    assert "PRIV-88" in doc.read_text(encoding="utf-8")  # the fact was never lost


def test_driver_accepts_a_safe_pass():
    doc = _tmp_copy(EX / "policy.md")
    checks = gate.load_facts_txt(FACTS)
    safe = lambda text: text + "\n<!-- tidied -->\n"  # noqa: E731  (keeps every fact)
    res = guarded_rewrite.run(doc, checks, safe, passes=3, retries=0, log=lambda *a: None)
    assert res["accepted"] == 3 and res["reverted"] == 0
    assert "<!-- tidied -->" in doc.read_text(encoding="utf-8")


if __name__ == "__main__":
    g = dict(globals())
    tests = sorted((k, v) for k, v in g.items() if k.startswith("test_") and callable(v))
    failed = []
    for name, fn in tests:
        try:
            fn(); print(f"  PASS {name}")
        except Exception as e:  # noqa: BLE001
            failed.append(name); print(f"  FAIL {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
