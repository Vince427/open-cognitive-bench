# Open Cognitive Bench — report

Run: `agentic-haiku-20260604-141005`
Task kinds: chesterton = regression

## Per-arm summary (failure rate, pooled across kinds)

| Arm | n | Failure rate | Artifact-cited | Mean $/run | Mean tokens | Mean latency (s) |
|---|---|---|---|---|---|---|
| B | 6 | 0.333 | 0.00 | $0.0000 | 0 | 0.000 |
| C | 6 | 0.000 | 0.00 | $0.0000 | 0 | 0.000 |
| S | 6 | 0.000 | 0.00 | $0.0000 | 0 | 0.000 |

## Pre-registered comparisons (pooled)

Bonferroni-corrected alpha = 0.05/5 = **0.0100**

| X vs Y | Δ failure (X−Y) | bootstrap 95% CI | McNemar p (n10/n01) | cost X/Y | verdict |
|---|---|---|---|---|---|
| S vs B | -0.333 | [-0.500, +0.000] | 0.5000 (0/2) | inf× | no sig. effect |
| C vs B | -0.333 | [-0.500, +0.000] | 0.5000 (0/2) | inf× | no sig. effect |

## Forest plot (negative ⇒ X failed less ⇒ X better; `*` = significant)

```
-1.0         (X−Y failure-rate difference)             +1.0
             -                   0                   +
S vs B                 [--o------]                     -0.333
C vs B                 [--o------]                     -0.333
```
_CI bar = bootstrap 95% CI; `o` = point estimate; `|`/`0` = no difference._

_Lower failure rate is better; negative Δ means X failed less than Y._
_Primary comparison is **W vs S**, interpreted net of the cost ratio. **S vs D** isolates the rule from prompt length._

