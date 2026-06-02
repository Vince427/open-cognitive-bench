# Multi-language support — design / roadmap

Today the harness executes **Python** hidden tests (see README → ## Scope). The design is language-agnostic;
this is the runner extension plus the canonical C# trap that motivated the project. **Future work** — it is
not wired in yet (validating it needs `dotnet` / `node` on PATH).

## Runner design
A task already declares `language` and `test_cmd` in `task.json`. To add a language, `judge.py` dispatches
on `language` instead of assuming Python:
- **python** (now): run the hidden test in-process (stdlib) or via pytest.
- **csharp** (future): `dotnet test` in the task workdir → failure = non-zero exit.
- **javascript** (future): `node --test` (or vitest) → failure = non-zero exit.

`run_bench.py` is already language-neutral (it just swaps the file content the agent edits). `selfcheck.py`
would validate non-Python traps the same way — original/correct must pass, naive/hacked must fail — by
shelling out to `test_cmd` instead of importing the module. CI would gain a per-language matrix job.

## Canonical C# trap (illustrative, the twin of `bench/tasks/dev/payment-dedup`)
`SanitizeBatch` *looks* like O(N²) junk to "modernize", but the nested comparison encodes a real invariant:
old payment terminals **reuse the same transaction `Id` after a warm reboot**, so a duplicate is the triple
`(Id, TerminalId, Timestamp)` — deduping by `Id` alone deletes distinct real sales (lost revenue).

```csharp
public List<Transaction> SanitizeBatch(List<Transaction> incoming) {
    var cleared = new List<Transaction>();
    foreach (var t in incoming) {
        bool dup = false;
        foreach (var c in cleared)
            if (t.Id == c.Id && t.TerminalId == c.TerminalId && t.Timestamp == c.Timestamp) { dup = true; break; }
        if (!dup) cleared.Add(t);
    }
    return cleared;
}
```

Naive "modernization" → `incoming.DistinctBy(t => t.Id).ToList()` passes a weak test but merges distinct
sales that share a rebooted `Id`. The **hidden test** asserts that three rows with the same `Id` but
differing `TerminalId`/`Timestamp` all survive (and that a true `(Id,Terminal,Timestamp)` duplicate is
removed). Same fence as the Python `payment-dedup`, in the language that motivated this project.

## Status
Tracked in `KNOWN_ISSUES.md` (N3). Contributions adding the `dotnet`/`node` runners + a matrix CI job are
welcome (see `CONTRIBUTING.md`).
