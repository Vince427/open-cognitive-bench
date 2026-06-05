"""Tests for the drift-guard integrations: the gate_all config runner, the MCP server, and the example
rewriter. Pure stdlib; run directly (exits non-zero on any failure) or under pytest:
    python drift-guard/integrations/test_integrations.py
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_all       # noqa: E402
import mcp_server      # noqa: E402
import example_rewriter  # noqa: E402

EX = HERE.parent / "example"


# ---- gate_all (the non-bypassable engine for the hook + CI) -----------------------------------------
def test_gate_all_passes_on_intact_config():
    with tempfile.TemporaryDirectory() as d:
        cfg = Path(d) / ".driftguard.json"
        cfg.write_text(json.dumps({"protect": [
            {"file": str(EX / "policy.md"), "facts": str(EX / "policy.facts.txt")},
            {"file": str(EX / "doc.py"), "checks": str(EX / "checks.py")},
        ]}), encoding="utf-8")
        assert gate_all.main([str(cfg)]) == 0


def test_gate_all_fails_when_a_fact_is_dropped():
    with tempfile.TemporaryDirectory() as d:
        cfg = Path(d) / ".driftguard.json"
        cfg.write_text(json.dumps({"protect": [
            {"file": str(EX / "policy_drifted.md"), "facts": str(EX / "policy.facts.txt")},
        ]}), encoding="utf-8")
        assert gate_all.main([str(cfg)]) == 1


def test_gate_all_no_config_is_noop():
    with tempfile.TemporaryDirectory() as d:
        assert gate_all.main([str(Path(d) / "absent.json")]) == 0


# ---- MCP server (the callable convenience) ----------------------------------------------------------
def test_mcp_initialize_echoes_protocol_and_reports_server():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                           "params": {"protocolVersion": "2025-06-18"}})
    assert r["result"]["protocolVersion"] == "2025-06-18"
    assert r["result"]["serverInfo"]["name"] == "drift-guard"
    assert "tools" in r["result"]["capabilities"]


def test_mcp_initialized_notification_gets_no_response():
    assert mcp_server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_mcp_tools_list_exposes_the_gate():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = r["result"]["tools"]
    assert tools[0]["name"] == "drift_guard_check"
    assert "facts" in tools[0]["inputSchema"]["properties"]


def test_mcp_tools_call_all_present():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
        "name": "drift_guard_check", "arguments": {"facts": ["90 days", "PRIV-88"],
                                                    "text": "retained 90 days under PRIV-88"}}})
    assert r["result"]["isError"] is False
    assert r["result"]["content"][0]["text"].startswith("2/2")


def test_mcp_tools_call_detects_missing_fact_and_regex():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
        "name": "drift_guard_check", "arguments": {"facts": ["90 days", r"re:GDPR Art\.?\s*17"],
                                                    "text": "kept 90 days only"}}})
    assert r["result"]["isError"] is True
    txt = r["result"]["content"][0]["text"]
    assert txt.startswith("1/2") and "MISSING" in txt


def test_mcp_tools_call_against_a_file():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
        "name": "drift_guard_check", "arguments": {"facts": ["90 days"], "file": str(EX / "policy.md")}}})
    assert r["result"]["isError"] is False


def test_mcp_tools_call_needs_exactly_one_of_text_or_file():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {
        "name": "drift_guard_check", "arguments": {"facts": ["x"]}}})  # neither text nor file
    assert r["result"]["isError"] is True


def test_mcp_unknown_method_is_method_not_found():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 7, "method": "no/such"})
    assert r["error"]["code"] == -32601


# ---- example rewriter (the offline stand-in for an LLM in the loop) ----------------------------------
def test_example_rewriter_drops_the_last_nonempty_line():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "doc.txt"
        p.write_text("alpha\nbeta\ngamma\n\n", encoding="utf-8")
        example_rewriter.main(str(p))
        assert "gamma" not in p.read_text(encoding="utf-8")
        assert "beta" in p.read_text(encoding="utf-8")


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
