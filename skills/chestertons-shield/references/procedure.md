# Chesterton's Shield — investigation procedure (detailed)

Concrete commands the agent should run and quote. The goal is **citable facts**, not narration.

## 1. History
```bash
git blame -L <start>,<end> -- <file>      # who/when/why per line
git log -p -S "<suspicious token>" -- <file>   # when was this branch/condition introduced
```
Look for: a commit message naming a bug/ticket, a "fix", a customer name, a hardware/firmware note.

## 2. Callers / blast radius
```bash
grep -rn "<functionName>" --include=*.{py,cs,ts,go} .
```
For each caller: what does it assume about the output? Does any caller rely on the "weird" branch?

## 3. Tests that lock behavior
```bash
grep -rln "<functionName>" **/test* **/*test*
```
Read them. A test that asserts a non-obvious output IS the encoded invariant. If there is NO test for the
weird branch, that is a finding too (the invariant is implicit and fragile — flag it).

## 4. Find the asymmetry
The hidden invariant almost always lives in the part that looks "wrong":
- a composite/compound key where a simple key would seem to suffice,
- nested `if`s that could "obviously" be flattened,
- an explicit special case, an off-by-one guard, a manual epsilon, a lock/order-of-operations.

Hypothesize: *"This exists because <X>; if I remove it, <concrete bad thing> happens."* Then confirm or
refute from steps 1–3 before touching anything.

## Anti-patterns (auto-fail the Fence Report)
- "This is just legacy code, safe to modernize." (no citation)
- "I'll add a try/catch / a comment and proceed." (patch over understanding)
- Rewriting the data-key to a *subset* of the original key (the classic regression).
