"""Pilot generator (provider = Claude Code subagents). Builds the EXACT per-(task,arm) prompts run_bench
would send, as standalone files under results/_pilot/prompts/, so an orchestrator (Claude Code) can dispatch
one subagent per cell as the 'model under test'. Real model behavior, no external API key. See README.md.

Outputs go under results/ (git-ignored). Run:  python bench/pilot/gen.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
import run_bench  # noqa: E402

PIL = ROOT / "results" / "_pilot"
(PIL / "prompts").mkdir(parents=True, exist_ok=True)
(PIL / "edits").mkdir(parents=True, exist_ok=True)

ARMS = ["B", "C", "D", "S"]   # solo arms; W (the 4-call workflow) is not covered by this simple pilot
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
print(f"{len(jobs)} jobs ({len(tasks)} dev tasks x {len(ARMS)} arms x {len(SEEDS)} seed); prompts -> {PIL / 'prompts'}")
