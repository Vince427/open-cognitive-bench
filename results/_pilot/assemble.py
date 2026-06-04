"""Assemble subagent-written edits into a run_bench-format run dir, so the existing judge.py + stats.py
can score it unchanged. Real-model DEV pilot — NOT the preregistered held-out run."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIL = ROOT / "results" / "_pilot"
jobs = json.loads((PIL / "jobs.json").read_text(encoding="utf-8"))

run_dir = ROOT / "results" / ("pilot-" + time.strftime("%Y%m%d-%H%M%S"))
run_dir.mkdir(parents=True, exist_ok=True)

recs, missing = [], []
for j in jobs:
    ep = Path(j["edit_path"])
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
    "provider": "claude-code-subagent-pilot",
    "note": "DEV pilot: real Claude Code subagents as the model under test, single-shot/no-tools. "
            "Single model, dev set, 1 seed. NOT the preregistered held-out run; do not report as RESULTS.",
    "arms": sorted({r["arm"] for r in recs}), "seeds": 1, "n_records": len(recs), "missing": missing,
}, indent=2), encoding="utf-8")
(ROOT / "results" / "latest").write_text(str(run_dir), encoding="utf-8")
print(f"assembled {len(recs)} records; missing {len(missing)}: {missing[:12]}")
print("run_dir:", run_dir)
