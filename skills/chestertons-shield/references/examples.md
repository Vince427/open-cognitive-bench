# Chesterton's Shield — before/after examples

## Example: payment-batch dedup (the canonical trap)

### The legacy code (looks bad)
An O(N²) double loop deduplicating transactions, comparing `Id`, then `TerminalId`, then `Timestamp` in
nested `if`s. Every instinct says: "replace with `DistinctBy(t => t.Id)`."

### The hidden invariant (the fence)
Old payment terminals re-emit the **same transaction `Id`** after a warm reboot (firmware counter reset).
So two rows with the same `Id` are duplicates **only if `TerminalId` AND `Timestamp` also match**. Same
`Id` + different terminal/time = **two real, distinct sales**. The nested conditions ARE the invariant.

### What an unguarded agent ships (regression — destroys revenue)
```csharp
public List<Transaction> SanitizeBatch(List<Transaction> txs)
    => txs.DistinctBy(t => t.Id).ToList();   // collapses distinct sales that share a colliding Id
```

### What Chesterton's Shield produces
**Fence Report**
- Likely reason it exists: commit `a91f3c2` "handle terminal reboot ID collision (ticket OPS-4471)" — terminals
  reset their counter and reuse IDs.
- Invariant to preserve: a duplicate ⇔ identical `(Id, TerminalId, Timestamp)`; same `Id` alone is NOT a duplicate.
- Evidence: `git blame` line on the inner `Timestamp` check → commit `a91f3c2`; caller `BankSubmitter` sums `Amount`.
- Decision: preserve invariant, optimize structure only.

```csharp
public List<Transaction> SanitizeBatch(List<Transaction> txs)
    => txs.GroupBy(t => (t.Id, t.TerminalId, t.Timestamp)).Select(g => g.First()).ToList(); // O(N), invariant intact
```

Same speed win (`O(N)` via hashing), **invariant preserved**. The difference is the **composite key**, which
only the investigation reveals.

> The Python version of this trap (runnable with the benchmark) is in `bench/tasks/dev/payment-dedup/`.
