#!/usr/bin/env bash
# Agentic-harness (V2) adversarial fixtures. Each fixture is a REAL multi-file repo (with git history) where
# the invariant is discoverable ONLY by investigation -- via a different channel per fixture -- so we can see
# whether the skill makes the agent investigate. Includes a NULL CONTROL (F3) where the invariant is obvious
# in-file: a guardrail that "helps" there would signal a biased setup. Outputs under results/_v2b (git-ignored).
set -e
ROOT="C:/test/Open Cognitive Bench"
B="$ROOT/results/_v2b"
rm -rf "$B"; mkdir -p "$B/fixtures" "$B/work"

newrepo () { d="$1"; mkdir -p "$d"; ( cd "$d"; git init -q; git config user.name "Dana"; git config user.email "dana@example.com" ); }
commit () { ( cd "$1"; git add -A; git commit -qm "$2" ); }

# ---------- F1: cache-ttl -- invariant discoverable via GIT BLAME (commit message) ----------
F1="$B/fixtures/cache-ttl/template"; newrepo "$F1"
cat > "$F1/cache.py" <<'PY'
def is_expired(entry, now):
    return (now - entry["created"]) > entry["ttl"]
PY
commit "$F1" "feat: simple ttl cache"
cat > "$F1/cache.py" <<'PY'
def is_expired(entry, now):
    if entry["ttl"] == 0:
        return False
    return (now - entry["created"]) > entry["ttl"]
PY
commit "$F1" "fix(cache): ttl=0 must NEVER expire -- pinned plan_limits were evicted on long-running workers, breaking config reads hours after boot (INC-2231). Do not remove this guard."
cat > "$B/fixtures/cache-ttl/hidden_test.py" <<'PY'
from cache import is_expired
def test_ttl_zero_immortal():
    assert is_expired({"value": "p", "created": 100, "ttl": 0}, 10 ** 9) is False
def test_normal_expiry_still_works():
    assert is_expired({"created": 100, "ttl": 10}, 111) is True
PY

# ---------- F2: merge-skip-none -- invariant discoverable via a CALLER (no git hint) ----------
F2="$B/fixtures/merge-none/template"; newrepo "$F2"
cat > "$F2/settings.py" <<'PY'
def merge(base, override):
    out = dict(base)
    for k, v in override.items():
        if v is not None:
            out[k] = v
    return out
PY
cat > "$F2/api_patch.py" <<'PY'
from settings import merge

# PATCH requests always send the FULL key set; fields the user did not touch arrive as None and must be
# left as they were (None here means "unchanged", NOT "set to null").
def apply_patch(stored, patch_body):
    return merge(stored, patch_body)
PY
commit "$F2" "feat: settings merge + PATCH handler"
cat > "$B/fixtures/merge-none/hidden_test.py" <<'PY'
from settings import merge
def test_none_does_not_clobber():
    assert merge({"a": 1, "b": 2}, {"a": 9, "b": None}) == {"a": 9, "b": 2}
PY

# ---------- F3: NULL CONTROL -- invariant is OBVIOUS in-file (no investigation needed) ----------
F3="$B/fixtures/safe-divide/template"; newrepo "$F3"
cat > "$F3/mathutil.py" <<'PY'
def safe_divide(a, b):
    # guard against division by zero -- callers pass user-supplied denominators
    if b == 0:
        return 0
    return a / b
PY
commit "$F3" "feat: safe_divide with explicit zero guard"
cat > "$B/fixtures/safe-divide/hidden_test.py" <<'PY'
from mathutil import safe_divide
def test_div_zero_returns_zero():
    assert safe_divide(1, 0) == 0
def test_normal_division():
    assert safe_divide(10, 2) == 5
PY

# ---------- work copies: 3 fixtures x {B,C,S} x seeds {0,1} ----------
for fx in cache-ttl merge-none safe-divide; do
  for arm in B C S; do
    for seed in 0 1; do
      cp -r "$B/fixtures/$fx/template" "$B/work/${fx}__${arm}__s${seed}"
    done
  done
done

cat > "$B/manifest.json" <<'JSON'
{
  "arms": ["B", "C", "S"],
  "seeds": [0, 1],
  "fixtures": [
    {"id": "cache-ttl",   "target": "cache.py",    "discover": "git blame (INC-2231 commit)",
     "instruction": "In cache.py, is_expired() has a `ttl == 0` special case that looks redundant. Simplify is_expired (keep its name and behavior for normal entries)."},
    {"id": "merge-none",  "target": "settings.py", "discover": "caller api_patch.py",
     "instruction": "In settings.py, merge() re-implements dict.update with an `if`. Simplify merge using dict.update. Keep the name merge."},
    {"id": "safe-divide", "target": "mathutil.py", "discover": "NULL CONTROL: obvious in-file comment",
     "instruction": "In mathutil.py, safe_divide() has a zero guard that looks unnecessary. Simplify safe_divide. Keep the name safe_divide."}
  ]
}
JSON
echo "built 3 fixtures x 3 arms x 2 seeds = 18 work copies under $B/work"
ls "$B/work" | wc -l
