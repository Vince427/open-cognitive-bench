# Results

> Template — fill after a real-model run. **No results have been collected yet** (the figures below are
> placeholders). Mock-provider runs are plumbing checks only and must NOT be reported here.

## Run metadata
- Date: `<fill>`
- Target model(s): `<e.g. claude-sonnet-4-5, gpt-4o>` · Lens/judge model (if different family): `<fill>`
- Temperature: `<fill>` · Seeds/arm: `<fill>` · Held-out tasks: `<N>` (`<n_chesterton>` chesterton + `<n_goodhart>` goodhart)
- Pre-registration frozen at commit: `<hash>`
- Reproduce: `./run.sh <provider> <model> bench/tasks/heldout <seeds>` (or `run.ps1`)

## Headline
`<one honest sentence: did W beat S on the held-out failure rate, and was it worth the cost? If not, say so.>`

## Per-arm summary (paste from `results/<run>/report.md`)
| Arm | n | Failure rate | Mean $/run | Mean tokens | Mean latency (s) |
|---|---|---|---|---|---|
| B | | | | | |
| C | | | | | |
| D | | | | | |
| S | | | | | |
| W | | | | | |

## By task kind
| Kind (failure = ) | B | C | D | S | W |
|---|---|---|---|---|---|
| chesterton (regression) | | | | | |
| goodhart (hack) | | | | | |

## Pre-registered comparisons
| X vs Y | Δ failure | bootstrap 95% CI | McNemar p | cost X/Y | verdict |
|---|---|---|---|---|---|
| W vs S (primary) | | | | | |
| S vs D (rule vs length) | | | | | |
| S vs B | | | | | |
| D vs B | | | | | |
| C vs B | | | | | |

## Interpretation & limitations
- `<W vs S net of the measured cost multiplier>`
- `<S vs D: is the effect the rule or just prompt length?>`
- Limitations: `<held-out authored by skill author? single language? models tested? judge calibration?>` —
  see `KNOWN_ISSUES.md`.

## Honesty
Per the project policy, this file is published **regardless of outcome**, including W not beating S or the
cost not being justified.
