# Quickstart — just use it

The plain, practical guide. No theory, no statistics, no math — for those just read
[`README.md`](README.md), [`drift-guard/README.md`](drift-guard/README.md) and [`PAPER.md`](PAPER.md).

There are **two things** you can use here. Pick what fits.

---

## 1. drift-guard — stop an AI from silently dropping facts when it re-edits a document

**Use it when:** you keep running a document through an LLM (condense, reword, refactor, "clean up") and you're
afraid it quietly loses something important — a constraint, a ticket number, a legal line, the *why*.

**Install:** nothing to install. It's plain Python (3.9+), no libraries, no API key. Just use the files in
[`drift-guard/`](drift-guard/) (copy that folder into your project, or run it where it is).

**Use it in 3 steps:**

```bash
# 1) List the facts that MUST survive — one per line (a word/phrase, or "re:" + a regex)
printf '90 days\nPRIV-88\nGDPR Art. 17\n' > facts.txt

# 2) Check a file — exit 0 = all facts present, exit 1 = something was lost
python drift-guard/gate.py --facts facts.txt --file mydoc.md

# 3) Gate a rewrite — overwrite mydoc.md ONLY if the new version still has every fact, else keep the old one
python drift-guard/gate.py --facts facts.txt --baseline mydoc.md --candidate new_version.md --apply mydoc.md
```

**Try it right now** (uses the shipped example — no setup):

```bash
python drift-guard/example/multipass_demo.py
# Shows one document edited 6 times: WITHOUT the gate it loses 3 of 5 facts; WITH the gate it keeps all 5.
```

**Automate the whole loop** (your own AI does the rewriting, the gate keeps it honest):

```bash
python drift-guard/guarded_rewrite.py --doc mydoc.md --facts facts.txt \
  --rewrite-cmd "your-ai-tool --condense" --passes 8
# Each pass: your tool rewrites -> the gate accepts it only if no fact was dropped, otherwise reverts.
```

That's it. More options (checking code *behavior*, not just text; drafting the fact list with an AI) are in
[`drift-guard/README.md`](drift-guard/README.md).

### Recipe: lock specific words/phrases to a file, and enforce it across the team

Three small files, then one install — after that, **any change that drops a listed phrase is rejected
automatically**, by code, with no human in the loop.

**1. The list** — `contract.facts.txt` (one phrase per line; prefix `re:` for a regex):
```
90 days
PRIV-88
GDPR Art. 17
```

**2. The mapping** — `.driftguard.json` at your repo root (file → its list; add as many files as you want):
```json
{ "protect": [
    { "file": "contract.md", "facts": "contract.facts.txt" }
] }
```

**3. The enforcer** — pick one (or several):
```bash
# local only: block the commit
cp drift-guard/integrations/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# whole team: block every push / PR — copy this workflow into your repo
cp drift-guard/integrations/github-actions.yml .github/workflows/drift-guard.yml

# AI agent self-check (MCP): the agent calls the gate before proposing a change
claude mcp add drift-guard -- python /abs/path/drift-guard/integrations/mcp_server.py
```

**Industrialize it for a team:**
- **Commit `.driftguard.json` and the `*.facts.txt` files into the repo** — the protected list is versioned
  and reviewed like any other code.
- **Use the CI workflow, not just the local hook.** Hooks aren't shared between clones and can be skipped
  with `git commit --no-verify`; CI runs for everyone and can't be bypassed. Every PR then shows a red build
  the instant a protected phrase disappears, and reviewers see exactly which one (`dropped: 90 days; …`).
- **To protect a new file, add one entry to `.driftguard.json`** — no code to write.
- Keep each `*.facts.txt` next to the doc it guards; let a domain owner approve the list once (an LLM can
  draft it — see `drift-guard/extract_facts_prompt.md`).

**Honest limit:** the gate checks a phrase is *present*, not that its *meaning* held — a rewrite that keeps
the words but negates them would pass. For meaning-level guarantees on **code**, use a behavioral checks
module (the `"checks"` key instead of `"facts"`). Details + all four enforcement modes:
[`drift-guard/integrations/`](drift-guard/integrations/README.md).

---

## 2. The Chesterton's Shield skill — make your AI coding agent look before it deletes

**Use it when:** your AI coding assistant tends to "simplify" or delete legacy code that turns out to be
load-bearing.

**Install (Claude Code):**

```
/plugin marketplace add Vince427/open-cognitive-bench
/plugin install chestertons-shield@open-cognitive-bench
```

**Install (anything else):** it's just a Markdown file. Copy it where your tool reads instructions
(e.g. a Cursor/Windsurf rule, or a project file `.claude/skills/chestertons-shield/SKILL.md`):

```
skills/chestertons-shield/SKILL.md
```

It makes the agent investigate *why* code exists (git history, callers, tests) before changing it.

> **One honest line:** this helps most when the agent is being pushed to "remove this, it looks redundant."
> A good model already investigates on its own when simply asked to refactor — so treat it as a useful
> safety net, not magic. (The full evidence is in [`PAPER.md`](PAPER.md).)

---

**Need more than this?** The full README has the benchmark, the evidence, and the honest limitations.
