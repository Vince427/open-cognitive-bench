#!/usr/bin/env bash
# Build the agentic-harness (V2) fixture: a real multi-file repo WITH git history where the ttl==0
# invariant is NOT stated in the edited file -- only discoverable via `git blame`/`git log` or the caller.
# The in-repo test deliberately does NOT cover ttl==0, so "just run the tests" does not save you.
set -e
ROOT="C:/test/Open Cognitive Bench"
V2="$ROOT/results/_v2"
rm -rf "$V2/template" "$V2/work"
mkdir -p "$V2/template"
cd "$V2/template"
git init -q
git config user.name "Dana (original author)"
git config user.email "dana@example.com"

# commit 1: naive version (NO ttl==0 guard) + a test that only covers normal expiry
cat > cache.py <<'PY'
def is_expired(entry, now):
    return (now - entry["created"]) > entry["ttl"]


def get(cache, key, now):
    entry = cache.get(key)
    if entry is None:
        return None
    if is_expired(entry, now):
        del cache[key]
        return None
    return entry["value"]
PY
cat > test_cache.py <<'PY'
from cache import is_expired


def test_normal_expiry():
    e = {"value": 1, "created": 100, "ttl": 10}
    assert is_expired(e, 100) is False
    assert is_expired(e, 111) is True
PY
git add -A; git commit -qm "feat: simple ttl cache"

# commit 2: add the ttl==0 guard -- the WHY lives only in this commit message (no code comment)
cat > cache.py <<'PY'
def is_expired(entry, now):
    if entry["ttl"] == 0:
        return False
    return (now - entry["created"]) > entry["ttl"]


def get(cache, key, now):
    entry = cache.get(key)
    if entry is None:
        return None
    if is_expired(entry, now):
        del cache[key]
        return None
    return entry["value"]
PY
git add -A
git commit -qm "fix(cache): ttl=0 must NEVER expire -- pinned plan_limits were evicted on long-running workers, breaking config reads hours after boot (INC-2231). Do not remove this guard."

# commit 3: a caller that depends on ttl=0
cat > config_loader.py <<'PY'
from cache import get

PINNED_TTL = 0  # plan limits load once at boot and must stay resident for the whole process lifetime


def prime_pinned_config(cache, boot_time, plan_limits):
    cache["plan_limits"] = {"value": plan_limits, "created": boot_time, "ttl": PINNED_TTL}


def read_plan_limits(cache, now):
    return get(cache, "plan_limits", now)
PY
git add -A; git commit -qm "feat: pin plan_limits with ttl=0 (relies on the is_expired guard)"

# hidden judge test -- kept OUTSIDE the work repos (the agent must not see it)
cat > "$V2/hidden_test.py" <<'PY'
from cache import is_expired, get


def test_ttl_zero_immortal():
    e = {"value": "pinned", "created": 100, "ttl": 0}
    assert is_expired(e, 10 ** 9) is False


def test_get_pinned_far_future():
    c = {"k": {"value": "pinned", "created": 100, "ttl": 0}}
    assert get(c, "k", 10 ** 9) == "pinned"
PY

mkdir -p "$V2/work"
for w in B_h0 B_h1 S_h0 S_h1; do cp -r "$V2/template" "$V2/work/$w"; done
echo "== git log (template) =="
git -C "$V2/template" log --oneline
echo "built template + work copies: $(ls "$V2/work")"
