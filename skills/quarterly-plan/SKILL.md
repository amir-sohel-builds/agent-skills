---
name: quarterly-plan
description: Build a quarter plan across teams: load against capacity, cross-team dependencies, and ordering checks. Use at planning time, when the question is whether the quarter actually fits, not whether it looks good on one page.
---

# Quarterly plan

## Inputs
- `examples/teams.json`: teams with people and hours per week.
- `examples/initiatives.json`: initiatives with a team, hours, a week, dependencies, and a priority.

## Run
```bash
python3 scripts/quarter.py --teams teams.json --initiatives initiatives.json --output QUARTER.md
```

## Output
A quarter plan: load against capacity by team and week, over-allocated teams, cross-team dependencies, ordering violations, and a summary.

## Rules
- A plan that fits in total but not in any single week is fiction. The week is the unit that slips.
- Cross-team dependencies are the plan. Everything else is a list.
- If a dependency is scheduled after the work that needs it, the plan is already late.
- Capacity is a constraint, not a target. Filling every hour is how a quarter slips.
- Priority does not change the math. A P0 that does not fit still does not fit.

## What it does not do
It does not decide priorities. It shows what the priorities cost, in hours and in weeks.
