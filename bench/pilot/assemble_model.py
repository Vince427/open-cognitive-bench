"""Assemble subagent-written edits from a chosen edits subdir into a run_bench-format run dir, so the
unmodified bench/judge.py + bench/stats.py score them. Real-model DEV pilot, NOT the held-out run.
Run:  python bench/pilot/assemble_model.py <edits_subdir> <label>   e.g.  ... edits_haiku haiku"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIL = ROOT / "results" / "_pilot"
edits_sub = sys.argv[1] if len(sys.argv) > 1 else "edits"
label = sys.argv[2] if len(sys.argv) > 2 else "subagent"

jobs = json.loads((PIL / "jobs.json").read_text(encoding="utf-8"))
run_dir = ROOT / "results" / (f"pilot-{label}-" + time.strftime("%Y%m%d-%H%M%S"))
run_dir.mkdir(parents=True, exist_ok=True)

recs, missing = [], []
for j in jobs:
    ep = PIL / edits_sub / f"{j['jid']}.py"
    if not ep.exists() or not ep.read_text(encoding="utf-8").strip():
        missing.append(j["jid"])
        continue
    code = ep.read_text(encoding="utf-8")
    recs.append({"task_id": j["task_id"], "kind": j["kind"], "arm": j["arm"], "seed": j["seed"],
                 "task_dir": j["task_dir"], "target_file": j["target_file"],
                 "response_text": code, "edited_code": code,
                 "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "latency_s": 0.0, "n_calls": 1})

(run_dir / "runs.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n", encoding="utf-8")
(run_dir / "meta.json").write_text(json.dumps({
    "provider": f"claude-code-subagent-pilot:{label}",
    "note": f"DEV pilot via Claude Code subagents (model={label}), single-shot/no-tools, 1 seed. "
            "NOT the preregistered held-out run.",
    "arms": sorted({r["arm"] for r in recs}), "seeds": 1, "n_records": len(recs), "missing": missing,
}, indent=2), encoding="utf-8")
(ROOT / "results" / "latest").write_text(str(run_dir), encoding="utf-8")
print(f"[{label}] assembled {len(recs)}; missing {len(missing)}: {missing[:12]}\nrun_dir: {run_dir}")
