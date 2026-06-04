"""Pilot generator: build the EXACT per-(task,arm) prompts run_bench would send, as standalone files,
so Claude Code subagents can play the 'model under test' on the DEV set. Real model behavior, not mock.
Gitignored (under results/). Single-shot/no-tools is enforced by the dispatcher, not here."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
import run_bench  # noqa: E402

PIL = ROOT / "results" / "_pilot"
(PIL / "prompts").mkdir(parents=True, exist_ok=True)
(PIL / "edits").mkdir(parents=True, exist_ok=True)

ARMS = ["B", "C", "D", "S"]   # solo arms; W (the 4-call workflow) deferred for the pilot
SEEDS = [0]

tasks = run_bench.discover_tasks(ROOT / "bench" / "tasks" / "dev")
jobs = []
for t in tasks:
    kind = t.get("kind", "chesterton")
    for arm in ARMS:
        for seed in SEEDS:
            system = run_bench.system_for(arm, kind)
            user = run_bench.base_user(t) + run_bench.RETURN_INSTRUCTION
            prompt = (system + "\n\n----- TASK -----\n\n" + user) if system else user
            jid = f"{t['id']}__{arm}__s{seed}"
            (PIL / "prompts" / f"{jid}.txt").write_text(prompt, encoding="utf-8")
            jobs.append({"jid": jid, "task_id": t["id"], "kind": kind, "arm": arm, "seed": seed,
                         "task_dir": t["_dir"], "target_file": t["target_file"],
                         "prompt_path": str(PIL / "prompts" / f"{jid}.txt"),
                         "edit_path": str(PIL / "edits" / f"{jid}.py")})

(PIL / "jobs.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
print(f"{len(jobs)} jobs ({len(tasks)} dev tasks x {len(ARMS)} arms x {len(SEEDS)} seed)")
print("arms:", ARMS, "| prompts dir:", PIL / "prompts")
