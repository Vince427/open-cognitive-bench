"""A FAKE 'condenser' rewriter so you can run the guarded-rewrite loop (Mode 2) offline, without an LLM.

`guarded_rewrite.py` invokes a rewrite command as:  <cmd> <candidate_path>  and expects it to edit the file
IN PLACE. This stub simulates a lossy "make it shorter" pass by deleting the last non-empty line each call —
eventually it tries to delete a fact-bearing line, and the gate reverts that pass. Replace this with your real
model CLI (e.g. `--rewrite-cmd "your-llm --condense"`); it is only here to make the loop demonstrable.

Usage (driven by guarded_rewrite, not directly):
  python drift-guard/guarded_rewrite.py --doc live.md --facts facts.txt \
    --rewrite-cmd "python drift-guard/integrations/example_rewriter.py" --passes 6
"""
import sys
from pathlib import Path


def main(path):
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()
    # drop the last non-empty line (a stand-in for "the model trimmed something it judged removable")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            del lines[i]
            break
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: example_rewriter.py <candidate_path>")
    main(sys.argv[1])
