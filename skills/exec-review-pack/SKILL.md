---
name: exec-review-pack
description: Build a one-page exec review pack from status, risks, and decisions. Use before an exec review, when leadership needs decisions, risks, and what changed, on one page, with nothing softened.
---

# Exec review pack

## Inputs
- A `workstreams.json` file (same shape as status-rollup), a `risks.json` file (same shape as risk-register), and a `decisions.json` file (same shape as decision-log). Examples are under `examples/`.

## Run
```bash
python3 scripts/pack.py --workstreams workstreams.json --risks risks.json --decisions decisions.json --since 2026-11-01 --output PACK.md
```

## Output
A one-page pack: decisions needed first, decisions since the given date, top risks, and what is on track. If nothing is red and no risk scores 15 or more, it says so in one line.

## Rules
- One page. If it does not fit, the program is not ready for an exec review.
- Decisions needed come first. Everything else is context.
- A risk with no owner is not a risk, it is a hope. It is named as one.
- No adjectives without a fact behind them. "Going well" is not an update, the milestone is.

## What it does not do
It does not soften bad news. It orders it: decisions first, risks second, progress last.
