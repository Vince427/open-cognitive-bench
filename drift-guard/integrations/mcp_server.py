"""drift-guard as an MCP tool — Mode 4 (the *callable* convenience).

A minimal Model Context Protocol server (stdio, newline-delimited JSON-RPC 2.0) that exposes the fact-gate as
a tool an MCP client (Claude Desktop, Claude Code, ...) can call — e.g. an agent that just rewrote a document
can self-check that it kept every load-bearing fact. Pure stdlib: NO `mcp` SDK, no dependencies, in keeping
with the rest of drift-guard.

> HONEST SCOPE: MCP makes the gate *callable*, not *guaranteed*. If the agent decides whether to honor a
> failed check, you are back to a soft nudge. For a real guarantee the gate must be a step that cannot be
> skipped — use the pre-commit hook or CI (`gate_all.py`), or the `guarded_rewrite.py` loop. Use this server
> for ergonomic agent self-checking *on top of* that, not instead of it.

Tool exposed:
  drift_guard_check(facts: string[], text?: string, file?: string)
    -> "<k>/<n> facts present" (+ MISSING list); isError=true if any listed fact is absent.

Run (for a client to spawn over stdio):  python drift-guard/integrations/mcp_server.py
Register in Claude Code:  claude mcp add drift-guard -- python /abs/path/drift-guard/integrations/mcp_server.py
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # drift-guard/ -> gate.py
import gate  # noqa: E402

SERVER_INFO = {"name": "drift-guard", "version": "0.1.0"}
DEFAULT_PROTOCOL = "2024-11-05"

TOOL = {
    "name": "drift_guard_check",
    "description": (
        "Check that load-bearing facts survive in a document (use after an LLM rewrite/condense). "
        "Returns how many of the listed facts are present and which are MISSING. "
        "Provide the facts plus EITHER the text to check OR a file path."
    ),
    "inputSchema": {
        "type": "object",
        "required": ["facts"],
        "properties": {
            "facts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Facts that must be present. A plain string = required literal substring; "
                               "a string starting with 're:' = a regex that must match.",
            },
            "text": {"type": "string", "description": "The document text to check (use this OR file)."},
            "file": {"type": "string", "description": "Path to a file to check (use this OR text)."},
        },
    },
}


def check(facts, text=None, file=None):
    """Return (k, n, missing[]) for the listed facts against text or file. Reuses the real gate engine."""
    with tempfile.TemporaryDirectory() as d:
        ff = Path(d) / "facts.txt"
        ff.write_text("\n".join(facts) + "\n", encoding="utf-8")
        checks = gate.load_facts_txt(ff)
        if file:
            target = Path(file)
            if not target.exists():
                raise FileNotFoundError(file)
        else:
            target = Path(d) / "doc.txt"
            target.write_text(text or "", encoding="utf-8")
        res = gate.run(target, checks)
    names = [n for n, _ in checks]
    missing = [n for n in names if not res[n]]
    return len(names) - len(missing), len(names), missing


def call_tool(name, args):
    """Return (text, is_error)."""
    if name != TOOL["name"]:
        return f"unknown tool: {name}", True
    facts = args.get("facts")
    if not isinstance(facts, list) or not facts:
        return "argument 'facts' must be a non-empty array of strings", True
    text, file = args.get("text"), args.get("file")
    if bool(text) == bool(file):
        return "provide exactly one of 'text' or 'file'", True
    try:
        k, n, missing = check(facts, text=text, file=file)
    except FileNotFoundError as e:
        return f"file not found: {e}", True
    msg = f"{k}/{n} facts present"
    if missing:
        msg += "  | MISSING: " + "; ".join(missing)
    return msg, bool(missing)


def handle(msg):
    """Dispatch one JSON-RPC message. Return a response dict, or None for notifications."""
    method, mid = msg.get("method"), msg.get("id")
    is_request = mid is not None

    if method == "initialize":
        proto = (msg.get("params") or {}).get("protocolVersion", DEFAULT_PROTOCOL)
        return _ok(mid, {"protocolVersion": proto, "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO})
    if method == "ping":
        return _ok(mid, {})
    if method == "tools/list":
        return _ok(mid, {"tools": [TOOL]})
    if method == "tools/call":
        params = msg.get("params") or {}
        text, is_error = call_tool(params.get("name"), params.get("arguments") or {})
        return _ok(mid, {"content": [{"type": "text", "text": text}], "isError": is_error})
    if method == "notifications/initialized" or not is_request:
        return None  # notification: no response
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}


def _ok(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
