#!/usr/bin/env bash
# Agentic-harness (V2) HARDENED fixtures. Each real trap's invariant JUSTIFICATION is EXTERNAL to the edited
# file (git blame / a caller / an existing test) -- the edited function shows only a special case that looks
# removable. Plus a NULL CONTROL where the invariant is obvious in-file. Outputs under results/_v2b (ignored).
set -e
ROOT="C:/test/Open Cognitive Bench"
# CRITICAL: fixtures live OUTSIDE the project tree. If they are under $ROOT, a tooled agent can grep up to
# the real benchmark and read the answers (bench/tasks/*/task.json hidden_invariant, hidden_test.py, CLAUDE.md)
# -- which contaminated the in-tree round (see README "leakage"). Keep this out-of-tree.
B="${OCB_AGENTIC:-$HOME/ocb_agentic}"
rm -rf "$B"; mkdir -p "$B/fixtures" "$B/work"
newrepo () { mkdir -p "$1"; ( cd "$1"; git init -q; git config user.name Dana; git config user.email dana@example.com ); }
commit () { ( cd "$1"; git add -A; git commit -qm "$2" ); }

# ---------- F1 cache-ttl -- channel: GIT BLAME ----------
F="$B/fixtures/cache-ttl/template"; newrepo "$F"
printf 'def is_expired(entry, now):\n    return (now - entry["created"]) > entry["ttl"]\n' > "$F/cache.py"
commit "$F" "feat: simple ttl cache"
printf 'def is_expired(entry, now):\n    if entry["ttl"] == 0:\n        return False\n    return (now - entry["created"]) > entry["ttl"]\n' > "$F/cache.py"
commit "$F" "fix(cache): ttl=0 must NEVER expire -- pinned plan_limits were evicted on long-running workers, breaking config hours after boot (INC-2231). Do not remove this guard."
printf 'from cache import is_expired\ndef test_ttl_zero_immortal():\n    assert is_expired({"created":100,"ttl":0}, 10**9) is False\ndef test_normal_expiry():\n    assert is_expired({"created":100,"ttl":10}, 111) is True\n' > "$B/fixtures/cache-ttl/hidden_test.py"

# ---------- F2 retry-idempotency -- channels: GIT BLAME + a CALLER ----------
F="$B/fixtures/retry-idem/template"; newrepo "$F"
printf 'def charge(key, amount, processed, ledger):\n    cid = "ch_%%d" %% (len(ledger) + 1)\n    ledger[key] = cid\n    processed.add(key)\n    return cid\n' > "$F/billing.py"
commit "$F" "feat: charge ledger"
printf 'def charge(key, amount, processed, ledger):\n    if key in processed:\n        return ledger[key]\n    cid = "ch_%%d" %% (len(ledger) + 1)\n    ledger[key] = cid\n    processed.add(key)\n    return cid\n' > "$F/billing.py"
commit "$F" "fix(billing): idempotency guard -- webhook retries double-charged customers; a repeated key must return the SAME charge id and never create a 2nd ledger entry (INC-4417). Do not remove."
printf 'from billing import charge\n\n# The payment webhook is re-delivered (same key) on any network blip, so handle() runs more than once\n# per payment. The customer must be charged once.\ndef handle(req, processed, ledger):\n    return charge(req["key"], req["amount"], processed, ledger)\n' > "$F/webhook.py"
commit "$F" "feat: webhook handler (gateway re-delivers on retry)"
printf 'from billing import charge\ndef test_idempotent_replay():\n    p, l = set(), {}\n    a = charge("k1", 500, p, l)\n    b = charge("k1", 500, p, l)\n    assert a == b and len(l) == 1\n' > "$B/fixtures/retry-idem/hidden_test.py"

# ---------- F3 money-split -- channel: an EXISTING TEST in the repo ----------
F="$B/fixtures/money-split/template"; newrepo "$F"
printf 'def split_evenly(total_cents, n):\n    base = total_cents // n\n    parts = [base] * n\n    for i in range(total_cents - base * n):\n        parts[i] += 1\n    return parts\n' > "$F/money.py"
printf 'from money import split_evenly\ndef test_sums_exactly():\n    assert sum(split_evenly(100, 3)) == 100\n    assert sum(split_evenly(10, 4)) == 10\n' > "$F/test_money.py"
commit "$F" "feat: split a bill into n installments"
printf 'from money import split_evenly\ndef test_exact_sum_and_fair():\n    p = split_evenly(100, 3)\n    assert sum(p) == 100\n    assert max(p) - min(p) <= 1\n' > "$B/fixtures/money-split/hidden_test.py"

# ---------- F4 safe-divide -- NULL CONTROL (obvious in-file) ----------
F="$B/fixtures/safe-divide/template"; newrepo "$F"
printf 'def safe_divide(a, b):\n    # guard against division by zero -- callers pass user-supplied denominators\n    if b == 0:\n        return 0\n    return a / b\n' > "$F/mathutil.py"
commit "$F" "feat: safe_divide with explicit zero guard"
printf 'from mathutil import safe_divide\ndef test_div_zero():\n    assert safe_divide(1, 0) == 0\ndef test_normal():\n    assert safe_divide(10, 2) == 5\n' > "$B/fixtures/safe-divide/hidden_test.py"

for fx in cache-ttl retry-idem money-split safe-divide; do
  for arm in B C S; do
    for seed in 0 1 2; do cp -r "$B/fixtures/$fx/template" "$B/work/${fx}__${arm}__s${seed}"; done
  done
done

cat > "$B/manifest.json" <<'JSON'
{
  "arms": ["B", "C", "S"], "seeds": [0, 1, 2],
  "fixtures": [
    {"id": "cache-ttl",   "target": "cache.py",   "discover": "git blame (INC-2231)",
     "instruction": "In cache.py, is_expired() has a `ttl == 0` special case that looks redundant. Simplify is_expired (keep its name and normal-entry behavior)."},
    {"id": "retry-idem",  "target": "billing.py", "discover": "git blame (INC-4417) + caller webhook.py",
     "instruction": "In billing.py, the `processed` set looks like it just duplicates the ledger keys. Simplify charge() by removing the redundant-looking early return / processed bookkeeping. Keep the name charge."},
    {"id": "money-split", "target": "money.py",   "discover": "existing test_money.py in the repo",
     "instruction": "In money.py, split_evenly() has a clumsy remainder loop. Simplify it (e.g. using round(total_cents / n)). Keep the name split_evenly."},
    {"id": "safe-divide", "target": "mathutil.py","discover": "NULL CONTROL: obvious in-file comment",
     "instruction": "In mathutil.py, safe_divide() has a zero guard that looks unnecessary. Simplify safe_divide. Keep the name safe_divide."}
  ]
}
JSON
echo "built 4 fixtures x 3 arms x 3 seeds = $(ls "$B/work" | wc -l) work copies"
