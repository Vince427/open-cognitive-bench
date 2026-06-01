#!/usr/bin/env bash
# Run the full Open Cognitive Bench pipeline (run_bench -> judge -> stats).
#   ./run.sh                                  # mock smoke test on the dev set
#   ./run.sh anthropic claude-sonnet-4-5
#   ./run.sh openai gpt-4o bench/tasks/heldout 5
set -euo pipefail

PROVIDER="${1:-mock}"
MODEL="${2:-}"
TASKS="${3:-bench/tasks/dev}"
SEEDS="${4:-5}"
ARMS="${5:-B C D S W}"

ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then echo "Python 3.11+ not found on PATH." >&2; exit 1; fi

ARGS=("$ROOT/bench/run_bench.py" --tasks "$ROOT/$TASKS" --arms $ARMS --seeds "$SEEDS" --provider "$PROVIDER")
if [ -n "$MODEL" ]; then ARGS+=(--model "$MODEL" --lens-model "$MODEL"); fi

"$PY" "${ARGS[@]}"
"$PY" "$ROOT/bench/judge.py" --run "$ROOT/results/latest"
"$PY" "$ROOT/bench/stats.py" --run "$ROOT/results/latest"
