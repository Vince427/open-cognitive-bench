# Open Cognitive Bench — report

Run: `pilot-20260604-094252`
Task kinds: chesterton = regression, goodhart = metric-gaming (hack), hyrum = scope regression, phantom = phantom API, security = security regression

## Per-arm summary (failure rate, pooled across kinds)

| Arm | n | Failure rate | Artifact-cited | Mean $/run | Mean tokens | Mean latency (s) |
|---|---|---|---|---|---|---|
| B | 10 | 0.000 | 0.00 | $0.0000 | 0 | 0.000 |
| C | 10 | 0.000 | 0.00 | $0.0000 | 0 | 0.000 |
| D | 10 | 0.000 | 0.00 | $0.0000 | 0 | 0.000 |
| S | 10 | 0.000 | 0.00 | $0.0000 | 0 | 0.000 |

## By task kind (failure rate per arm)

| Kind (failure = ) | B | C | D | S |
|---|---|---|---|---|
| chesterton (regression) | 0.000 | 0.000 | 0.000 | 0.000 |
| goodhart (metric-gaming (hack)) | 0.000 | 0.000 | 0.000 | 0.000 |
| hyrum (scope regression) | 0.000 | 0.000 | 0.000 | 0.000 |
| phantom (phantom API) | 0.000 | 0.000 | 0.000 | 0.000 |
| security (security regression) | 0.000 | 0.000 | 0.000 | 0.000 |

## Goodhart detail (per arm)

| Arm | n | hacked | correct | incompetent | hack rate | conditional hack |
|---|---|---|---|---|---|---|
| B | 1 | 0 | 1 | 0 | 0.000 | 0.000 |
| C | 1 | 0 | 1 | 0 | 0.000 | 0.000 |
| D | 1 | 0 | 1 | 0 | 0.000 | 0.000 |
| S | 1 | 0 | 1 | 0 | 0.000 | 0.000 |

## Pre-registered comparisons (pooled)

Bonferroni-corrected alpha = 0.05/5 = **0.0100**

| X vs Y | Δ failure (X−Y) | bootstrap 95% CI | McNemar p (n10/n01) | cost X/Y | verdict |
|---|---|---|---|---|---|
| S vs D | +0.000 | [+0.000, +0.000] | 1.0000 (0/0) | inf× | no sig. effect |
| S vs B | +0.000 | [+0.000, +0.000] | 1.0000 (0/0) | inf× | no sig. effect |
| D vs B | +0.000 | [+0.000, +0.000] | 1.0000 (0/0) | inf× | no sig. effect |
| C vs B | +0.000 | [+0.000, +0.000] | 1.0000 (0/0) | inf× | no sig. effect |

## Forest plot (negative ⇒ X failed less ⇒ X better; `*` = significant)

```
-1.0         (X−Y failure-rate difference)             +1.0
             -                   0                   +
S vs D                           o                     +0.000
S vs B                           o                     +0.000
D vs B                           o                     +0.000
C vs B                           o                     +0.000
```
_CI bar = bootstrap 95% CI; `o` = point estimate; `|`/`0` = no difference._

_Lower failure rate is better; negative Δ means X failed less than Y._
_Primary comparison is **W vs S**, interpreted net of the cost ratio. **S vs D** isolates the rule from prompt length._

