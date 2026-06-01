"""Open Cognitive Bench — run the 4 arms (B/C/S/W) over a task set, multi-seed, paired.

Produces results/<run>/runs.jsonl (one record per task x arm x seed) plus meta.json, and writes the run
path into results/latest so judge.py / stats.py can pick it up with `--run results/latest`.

Usage:
    python bench/run_bench.py --tasks bench/tasks/dev --arms B C S W --seeds 5 --provider mock
"""
from __future__ import annotations
import argparse
import json
import re
import time
from pathlib import Path

from providers import get_provider

ROOT = Path(__file__).resolve().parent.parent          # repo root
BENCH = ROOT / "bench"
RESULTS = ROOT / "results"

SKILL_CHESTERTON = (ROOT / "skills" / "chestertons-shield" / "SKILL.md").read_text(encoding="utf-8")
SKILL_GOODHART = (ROOT / "skills" / "goodhart-attack" / "SKILL.md").read_text(encoding="utf-8")

RETURN_INSTRUCTION = "\n\nReturn the COMPLETE updated file in a single ```python code block, nothing else."

SYNTH_SYS = (
    "You are a skeptical synthesizer. Read the lens reports. List the concrete invariants that MUST be "
    "preserved and the metric-gaming risks. Output a short gate decision PASS/BLOCK and the invariants."
)
IMPL_SYS = "You are a careful implementer. Apply the requested change while preserving every listed invariant."

CODE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


def extract_code(text: str, fallback: str) -> str:
    blocks = CODE_RE.findall(text or "")
    if blocks:
        return blocks[-1].strip("\n") + "\n"
    return (text or fallback)


def discover_tasks(tasks_dir: Path):
    tasks = []
    for tj in sorted(tasks_dir.rglob("task.json")):
        meta = json.loads(tj.read_text(encoding="utf-8"))
        meta["_dir"] = str(tj.parent)
        meta["_original"] = (tj.parent / meta["target_file"]).read_text(encoding="utf-8")
        tasks.append(meta)
    return tasks


def base_user(task):
    return f"{task['instruction']}\n\nFILE `{task['target_file']}`:\n```python\n{task['_original']}```"


def run_solo(provider, task, seed, system, arm, model):
    user = base_user(task) + RETURN_INSTRUCTION
    r = provider.complete(system, user, model=model, seed=seed,
                          meta={"arm": arm, "task_id": task["id"], "original": task["_original"], "role": "main"})
    return r["text"], [r]


def run_workflow(provider, task, seed, model, lens_model):
    ctx = base_user(task)
    calls = []
    r_ch = provider.complete("Investigate why this code exists.\n\n" + SKILL_CHESTERTON, ctx,
                             model=lens_model, seed=seed,
                             meta={"arm": "W", "task_id": task["id"], "role": "lens_chesterton"})
    r_gh = provider.complete("Red-team how a change here games the tests.\n\n" + SKILL_GOODHART, ctx,
                             model=lens_model, seed=seed,
                             meta={"arm": "W", "task_id": task["id"], "role": "lens_goodhart"})
    r_sy = provider.complete(SYNTH_SYS, ctx + "\n\nLENS A:\n" + r_ch["text"] + "\n\nLENS B:\n" + r_gh["text"],
                             model=lens_model, seed=seed,
                             meta={"arm": "W", "task_id": task["id"], "role": "synth"})
    impl_user = (base_user(task) + "\n\nInvariants to preserve (from the gate):\n" + r_sy["text"]
                 + RETURN_INSTRUCTION)
    r_im = provider.complete(IMPL_SYS, impl_user, model=model, seed=seed,
                             meta={"arm": "W", "task_id": task["id"], "original": task["_original"], "role": "main"})
    calls = [r_ch, r_gh, r_sy, r_im]
    return r_im["text"], calls


ARM_SYSTEMS = {
    "B": "",
    "C": "Be careful not to break any existing behavior when you change this code.",
    "S": SKILL_CHESTERTON,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--arms", nargs="+", default=["B", "C", "S", "W"])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--provider", default="mock")
    ap.add_argument("--model", default=None)
    ap.add_argument("--lens-model", default=None)
    args = ap.parse_args()

    provider = get_provider(args.provider)
    lens_model = args.lens_model or args.model
    tasks = discover_tasks(Path(args.tasks).resolve())
    if not tasks:
        raise SystemExit(f"no task.json found under {args.tasks}")

    run_id = "run-" + time.strftime("%Y%m%d-%H%M%S")
    run_dir = RESULTS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for task in tasks:
        for arm in args.arms:
            for seed in range(args.seeds):
                t0 = time.time()
                if arm == "W":
                    text, calls = run_workflow(provider, task, seed, args.model, lens_model)
                else:
                    text, calls = run_solo(provider, task, seed, ARM_SYSTEMS[arm], arm, args.model)
                edited = extract_code(text, task["_original"])
                rec = {
                    "task_id": task["id"], "arm": arm, "seed": seed,
                    "task_dir": task["_dir"], "target_file": task["target_file"],
                    "response_text": text, "edited_code": edited,
                    "input_tokens": sum(c["input_tokens"] for c in calls),
                    "output_tokens": sum(c["output_tokens"] for c in calls),
                    "cost_usd": sum(c["cost_usd"] for c in calls),
                    "latency_s": round(time.time() - t0, 4),
                    "n_calls": len(calls),
                }
                records.append(rec)
                print(f"  {task['id']:16s} {arm} seed={seed} calls={len(calls)} ${rec['cost_usd']:.4f}")

    (run_dir / "runs.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    (run_dir / "meta.json").write_text(json.dumps({
        "provider": args.provider, "model": args.model, "lens_model": lens_model,
        "arms": args.arms, "seeds": args.seeds, "tasks": [t["id"] for t in tasks],
        "n_records": len(records),
    }, indent=2), encoding="utf-8")
    (RESULTS / "latest").write_text(str(run_dir), encoding="utf-8")
    print(f"\nWrote {len(records)} records -> {run_dir}")
    print(f"results/latest -> {run_dir}")


if __name__ == "__main__":
    main()
