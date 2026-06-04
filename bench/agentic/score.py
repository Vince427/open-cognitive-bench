"""Score the agentic-harness work copies: run each fixture's hidden test against the edited target file,
print a fixture x arm failure matrix, and emit judgments.jsonl (+ meta) so bench/stats.py can run McNemar.
Usage: python bench/agentic/score.py [label]   (reads results/_v2b/{manifest.json,work/,fixtures/})"""
import importlib.util as u
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "results" / "_v2b"
man = json.loads((B / "manifest.json").read_text(encoding="utf-8"))
label = sys.argv[1] if len(sys.argv) > 1 else "agentic"


def run_hidden(target_name, target_src, hidden_src):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / target_name).write_text(target_src, encoding="utf-8")
        (d / "hidden_test.py").write_text(hidden_src, encoding="utf-8")
        sys.path.insert(0, str(d))
        for m in (Path(target_name).stem, "hidden_test"):
            sys.modules.pop(m, None)
        fails = []
        try:
            s = u.spec_from_file_location("hidden_test", str(d / "hidden_test.py"))
            mod = u.module_from_spec(s); s.loader.exec_module(mod)
            for n in sorted(dir(mod)):
                if n.startswith("test_"):
                    try:
                        getattr(mod, n)()
                    except Exception as e:  # noqa: BLE001
                        fails.append(f"{n}<{type(e).__name__}>")
        except Exception as e:  # noqa: BLE001
            fails.append(f"COLLECT<{type(e).__name__}>")
        finally:
            sys.path.remove(str(d))
        return fails


arms, seeds = man["arms"], man["seeds"]
judgments = []
matrix = {}   # (fid, arm) -> [failed bools]
missing = []
for fx in man["fixtures"]:
    fid, target = fx["id"], fx["target"]
    hidden = (B / "fixtures" / fid / "hidden_test.py").read_text(encoding="utf-8")
    for arm in arms:
        for seed in seeds:
            wt = B / "work" / f"{fid}__{arm}__s{seed}" / target
            if not wt.exists():
                missing.append(f"{fid}__{arm}__s{seed}")
                continue
            fails = run_hidden(target, wt.read_text(encoding="utf-8"), hidden)
            failed = len(fails) > 0
            matrix.setdefault((fid, arm), []).append(failed)
            judgments.append({"task_id": fid, "kind": "chesterton", "arm": arm, "seed": seed,
                              "failed": failed, "detail": "regression" if failed else "ok",
                              "artifact_ok": False, "cost_usd": 0.0, "latency_s": 0.0,
                              "input_tokens": 0, "output_tokens": 0})

# ---- print the fixture x arm failure matrix (the real readout; n is tiny) ----
print(f"\nFailure rate per fixture x arm (lower = better; {len(seeds)} seeds each):\n")
hdr = f"{'fixture':16s} " + " ".join(f"{a:>6s}" for a in arms) + "   discover"
print(hdr); print("-" * len(hdr))
disc = {f["id"]: f["discover"] for f in man["fixtures"]}
for fx in man["fixtures"]:
    fid = fx["id"]
    cells = []
    for a in arms:
        v = matrix.get((fid, a), [])
        cells.append(f"{(sum(v) / len(v)):.2f}" if v else "  -  ")
    print(f"{fid:16s} " + " ".join(f"{c:>6s}" for c in cells) + f"   {disc[fid]}")
print()
for a in arms:
    allv = [b for (fid, arm), v in matrix.items() if arm == a for b in v]
    print(f"  arm {a}: pooled failure {sum(allv)}/{len(allv)} = {sum(allv)/len(allv):.2f}" if allv else f"  arm {a}: -")

run_dir = ROOT / "results" / (f"agentic-{label}-" + time.strftime("%Y%m%d-%H%M%S"))
run_dir.mkdir(parents=True, exist_ok=True)
(run_dir / "judgments.jsonl").write_text("\n".join(json.dumps(j) for j in judgments) + "\n", encoding="utf-8")
(run_dir / "meta.json").write_text(json.dumps({
    "provider": f"claude-code-subagent-agentic:{label}", "arms": arms, "seeds": len(seeds),
    "note": "Agentic V2 harness: tooled subagents on planted repos; invariant discoverable only by "
            "investigation. PROTOTYPE -- single author wrote skill+fixture+judge; not significant.",
    "fixtures": [f["id"] for f in man["fixtures"]], "missing": missing, "n": len(judgments),
}, indent=2), encoding="utf-8")
(ROOT / "results" / "latest").write_text(str(run_dir), encoding="utf-8")
print(f"\nmissing: {len(missing)} {missing[:6]}\nrun_dir: {run_dir}")
