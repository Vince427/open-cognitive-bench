# drift-guard integrations — four ways to actually run the gate

A skill is a *prompt*; it can't execute anything, so it can only **reduce** drift, never guarantee it. The
guarantee comes from **running the gate**. Here are the ways to run it, ordered by how non-bypassable they are
— which is exactly how strong the guarantee is.

| Mode | Who runs the gate | Bypassable? | Use it for |
|---|---|---|---|
| 1a. **CI** | your CI on every push/PR | ❌ no — build goes red | the real guarantee, team-wide |
| 1b. **pre-commit hook** | git, before each commit | ❌ no (unless `--no-verify`) | the real guarantee, local |
| 2. **guarded-rewrite loop** | `guarded_rewrite.py` drives your LLM | ❌ no — the script reverts | automated multi-pass rewriting |
| 3. **agent runs the CLI** | the agent, told by the Skill | 🟡 soft — agent may ignore a failure | best-effort self-check in-agent |
| 4. **MCP tool** | an MCP client calls `drift_guard_check` | 🟡 soft — agent may ignore a failure | ergonomic agent self-check |

> **The one rule:** a *guarantee* requires the gate to be a step that **rejects** and cannot be skipped
> (modes 1 and 2). Modes 3 and 4 make the gate *callable* by an agent — useful, but if the agent decides
> whether to honor a failed check, it is back to a soft nudge. Use 3/4 **on top of** 1/2, not instead.

Everything here is **pure stdlib** — no `pip install`, no API key.

---

## Modes 1a / 1b — CI and pre-commit (the real guarantee)

Both read a `.driftguard.json` at your repo root listing the files to protect (see
[`.driftguard.json.example`](.driftguard.json.example)):

```json
{
  "protect": [
    { "file": "docs/policy.md", "facts":  "docs/policy.facts.txt" },
    { "file": "src/cache.py",   "checks": "tests/cache.checks.py" }
  ]
}
```

`gate_all.py` gates every entry and exits non-zero if any file dropped a fact:

```bash
python drift-guard/integrations/gate_all.py .driftguard.json
```

**CI:** copy [`github-actions.yml`](github-actions.yml) to `.github/workflows/drift-guard.yml`. The build
fails the moment a protected fact disappears.

**pre-commit (plain git hook):**
```bash
cp drift-guard/integrations/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
**pre-commit ([framework](https://pre-commit.com)):** this repo ships a [`.pre-commit-hooks.yaml`](.pre-commit-hooks.yaml);
add it to your `.pre-commit-config.yaml` (see that file's header).

---

## Mode 2 — the guarded-rewrite loop

Let your model rewrite, and let the gate accept-or-revert each pass automatically. Plug your model in as
`--rewrite-cmd` (invoked as `<cmd> <candidate_path>`, editing the file in place):

```bash
python drift-guard/guarded_rewrite.py --doc live.md --facts facts.txt \
  --rewrite-cmd "your-llm-cli --condense" --passes 8 --retries 1
```

Try it offline with the bundled fake "condenser" ([`example_rewriter.py`](example_rewriter.py), which just
trims the last line each pass):

```bash
cp drift-guard/example/policy.md live.md
python drift-guard/guarded_rewrite.py --doc live.md --facts drift-guard/example/policy.facts.txt \
  --rewrite-cmd "python drift-guard/integrations/example_rewriter.py" --passes 6 --retries 0
# Here every pass would drop a fact, so every pass is REVERTED -> all 5 facts survive. With a real model
# most passes are safe and get accepted; the gate only reverts the lossy ones (see example/multipass_demo.py).
```

---

## Mode 3 — the agent runs the CLI (the Skill)

Give the agent the [`../SKILL.md`](../SKILL.md) ("Drift Shield") and it will run `gate.py` itself after a
rewrite (any agent with a shell tool: Claude Code, Cursor, ...). Honest: this is best-effort — the agent
*could* ignore a failed gate, which is why modes 1/2 exist.

---

## Mode 4 — MCP tool (`mcp_server.py`)

A minimal MCP server (stdio, JSON-RPC, pure stdlib — no `mcp` SDK) exposing one tool, `drift_guard_check`,
so an MCP client can self-check a rewrite:

```
drift_guard_check(facts: string[], text?: string, file?: string)
  -> "<k>/<n> facts present" (+ MISSING list); isError=true if any listed fact is absent.
```

Register it in Claude Code:
```bash
claude mcp add drift-guard -- python /ABS/PATH/drift-guard/integrations/mcp_server.py
```
Or in any MCP client, spawn `python drift-guard/integrations/mcp_server.py` over stdio.

> Same caveat as Mode 3: MCP makes the gate *callable*, not *guaranteed*. Pair it with Mode 1 or 2 for the
> guarantee.

---

## Edge cases & FAQ

**First, the thing people worry about most:** *"won't it block on some other file that happens to contain the
same text?"* — **No.** The gate is scoped to the `(file → facts)` pairs you declare in `.driftguard.json`. It
only ever checks the files you list, each against its own list. A different file with the same words is never
looked at. There is no repo-wide text scan.

| Twisted case | What happens | What to do |
|---|---|---|
| A protected fact must **legitimately change** (e.g. `90 days` → `60 days`) | the gate blocks | Update that line in the `*.facts.txt` **in the same commit/PR**. The list is versioned and reviewed, so the change is explicit — that's the point, not a bug. |
| **Whitespace / formatting** drift (`GDPR Art. 17` → `GDPR  Art.17`, or a line break) | a literal match breaks | Use a tolerant regex: `re:GDPR\s*Art\.?\s*17`. |
| **Over-match** (`90 days` also matches inside `190 days`) | false "present" | Use word boundaries: `re:\b90 days\b`. |
| Content **moves to another file** | the original file lost it → blocks (even though nothing was lost overall) | The gate is per-file by design. Point `.driftguard.json` at the new file (same PR). "Must exist *somewhere* in the repo" is deliberately out of scope. |
| Protected file **renamed / deleted** | `gate_all` reports `file is missing` → blocks | Intended (don't silently drop a protected doc). If deliberate, update the mapping. |
| A fact that is **too generic** (`data`, `API`) | present everywhere → passes trivially (false safety) | List distinctive phrases (a ticket id, a constant, a clause). |
| A fact **moves *within* the same file** (real line deleted, but the string still appears elsewhere in that file) | passes (string present, just relocated) | "presence, not position." For structural guarantees use a behavioral `--checks` module (assert the section/predicate holds), not a word list. |

**The principle that resolves every case** — two clean rules:
1. The gate knows **only** the `(file → facts)` pairs you declare; nothing else in the repo exists for it.
2. When a protected fact legitimately changes or moves, you **update the declared list in the same commit** —
   and the reviewer sees it.

Because it is **deterministic**, there is never a mysterious block: the output names exactly which fact in
which file is missing (`FAIL contract.md | dropped: 90 days`). Every "false block" is really a *real change to
a protected fact* surfaced for review — which is exactly what you wanted.

## Tests

```bash
python drift-guard/integrations/test_integrations.py   # gate_all + MCP server + example rewriter (in CI)
```
