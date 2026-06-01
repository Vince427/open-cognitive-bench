"""Model-provider abstraction for Open Cognitive Bench.

Every provider.complete(...) returns a dict:
    {"text", "input_tokens", "output_tokens", "cost_usd", "latency_s"}

The `mock` provider is deterministic (seeded) and spends nothing — it exists to validate the harness and
the statistics end-to-end. It is NOT evidence about real models.
"""
from __future__ import annotations
import time
import random

# Rough USD per 1M tokens (input, output). Override per model as needed.
PRICES = {"default": (3.0, 15.0)}


def _price(model: str):
    return PRICES.get(model, PRICES["default"])


def get_provider(name: str):
    name = (name or "mock").lower()
    if name == "mock":
        return MockProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "openai":
        return OpenAIProvider()
    raise ValueError(f"unknown provider: {name}")


class AnthropicProvider:
    name = "anthropic"

    def __init__(self):
        import anthropic  # lazy
        self.client = anthropic.Anthropic()

    def complete(self, system, user, model=None, seed=0, meta=None):
        model = model or "claude-3-5-sonnet-latest"
        t0 = time.time()
        msg = self.client.messages.create(
            model=model, max_tokens=2048, system=system or "",
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(getattr(b, "text", "") for b in msg.content)
        it, ot = msg.usage.input_tokens, msg.usage.output_tokens
        pin, pout = _price(model)
        return {"text": text, "input_tokens": it, "output_tokens": ot,
                "cost_usd": it / 1e6 * pin + ot / 1e6 * pout, "latency_s": time.time() - t0}


class OpenAIProvider:
    name = "openai"

    def __init__(self):
        from openai import OpenAI  # lazy
        self.client = OpenAI()

    def complete(self, system, user, model=None, seed=0, meta=None):
        model = model or "gpt-4o"
        t0 = time.time()
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": user})
        resp = self.client.chat.completions.create(model=model, messages=msgs, seed=seed, max_tokens=2048)
        text = resp.choices[0].message.content or ""
        it = resp.usage.prompt_tokens
        ot = resp.usage.completion_tokens
        pin, pout = _price(model)
        return {"text": text, "input_tokens": it, "output_tokens": ot,
                "cost_usd": it / 1e6 * pin + ot / 1e6 * pout, "latency_s": time.time() - t0}


# --------------------------------------------------------------------------------------
# Mock provider
# --------------------------------------------------------------------------------------
# Per-task "naive bad rewrite" that breaks the hidden invariant (what an unguarded agent ships).
BAD_REWRITES = {
    "payment-dedup": (
        "from dataclasses import dataclass\n\n\n"
        "@dataclass\nclass Transaction:\n    id: str\n    amount: float\n    timestamp: str\n    terminal_id: str\n\n\n"
        "def sanitize_batch(incoming):\n"
        "    seen = set()\n    out = []\n    for t in incoming:\n"
        "        if t.id not in seen:\n            seen.add(t.id)\n            out.append(t)\n    return out\n"
    ),
    "cache-ttl": (
        'def is_expired(entry, now):\n    return (now - entry["created"]) > entry["ttl"]\n\n\n'
        'def get(cache, key, now):\n    entry = cache.get(key)\n    if entry is None:\n        return None\n'
        '    if is_expired(entry, now):\n        del cache[key]\n        return None\n    return entry["value"]\n'
    ),
    "money-rounding": (
        "def split_installments(total_cents, n):\n    return [round(total_cents / n)] * n\n"
    ),
    "config-bool": (
        "def parse_bool(s):\n    return bool(s)\n"
    ),
    "retry-idempotency": (
        "def process_payment(key, amount, processed, ledger):\n"
        '    charge_id = "chg_%d" % (len(ledger) + 1)\n'
        "    ledger[key] = charge_id\n    return charge_id\n"
    ),
    "business-days": (
        "from datetime import timedelta\n\n\n"
        "def add_business_days(start, n):\n    return start + timedelta(days=n)\n"
    ),
    "pagination-clamp": (
        "def page(items, page_num, size):\n    start = (page_num - 1) * size\n"
        "    return items[start:start + size]\n"
    ),
    "version-compare": (
        "def version_ge(a, b):\n    return a >= b\n"
    ),
}

# Probability the arm ships the invariant-breaking rewrite (mock behavior model only).
# Illustrative pattern mirroring Open Collider's finding: a bare instruction (C) and a verbose length/context
# brief (D) help only modestly, while the structured skill (S) and the gating workflow (W) help a lot.
BREAK_PROB = {"B": 0.85, "C": 0.65, "D": 0.55, "S": 0.20, "W": 0.10}

_FENCE = (
    "# Fence Report\n"
    "# Likely reason it exists: commit a91f3c2 handles a hardware/firmware edge case (mock citation).\n"
    "# Invariant to preserve: the composite key / sentinel must not be collapsed.\n"
    "# Evidence: hidden invariant locked by the covering test (mock).\n"
    "# Decision: preserve invariant, optimize structure only.\n"
)


class MockProvider:
    name = "mock"

    def _mk(self, text, it, ot):
        pin, pout = _price("default")
        return {"text": text, "input_tokens": it, "output_tokens": ot,
                "cost_usd": it / 1e6 * pin + ot / 1e6 * pout, "latency_s": 0.0}

    def complete(self, system, user, model=None, seed=0, meta=None):
        meta = meta or {}
        role = meta.get("role", "main")
        arm = meta.get("arm", "B")
        task_id = meta.get("task_id", "")
        original = meta.get("original", "")
        # Lens / synthesizer roles: cheap structured text, no code (they add the W cost multiplier).
        if role in ("lens_chesterton", "lens_goodhart", "synth"):
            return self._mk(f"[mock {role}] preserve the hidden invariant for {task_id}.", 320, 90)
        # Implementer / single-agent: decide break vs preserve, deterministically per (arm,task,seed).
        rng = random.Random(f"{arm}|{task_id}|{seed}")
        broke = rng.random() < BREAK_PROB.get(arm, 0.5)
        if broke and task_id in BAD_REWRITES:
            code = BAD_REWRITES[task_id]
            prose = ""
        else:
            code = original  # echoing the (correct) original passes the hidden test
            prose = _FENCE if arm in ("S", "W") else ""
        text = f"{prose}\n```python\n{code}\n```\n"
        return self._mk(text, 640, 360)
