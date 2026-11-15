---
name: capacity-plan
description: Match committed work against team capacity, by person and by week. Use during planning, when the question is whether the team can actually do what is committed.
---

# Capacity plan

## Inputs
- `examples/capacity.json` shows the shape: people with hours per week, and work items with an owner, hours, and a week.

## Run
```bash
python3 scripts/capacity.py --input capacity.json
```

## Output
A table per week: committed hours against available hours, per person. OVER means committed is above available. UNDER means committed is under half of available. The script exits 1 when anyone is over.

## Rules
- Hours are the only unit. No points, no t-shirts, no vibes.
- Over-allocation is a fact, not a feeling. If the table says OVER, something moves: scope, date, or owner.
- Under half is flagged too. An idle owner is a plan that forgot someone.

## What it does not do
It does not estimate the work. It checks the math on estimates the owners already gave.
