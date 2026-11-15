---
name: stakeholder-update
description: Turn the status file into a one-page exec update. Use when leadership needs the same facts as the team, shorter, with risks first and decisions named.
---

# Stakeholder update

## Inputs
- The same `workstreams.json` the status-rollup reads: name, owner, status of green, amber, or red, next milestone, blockers.

## Run
```bash
python3 scripts/update.py --input workstreams.json --output UPDATE.md
```

## Output
A one-page update: decisions needed first, then at risk, then on track. Red items name their blocker and owner. If nothing is red, it says so in one line.

## Rules
- Decisions needed come first. Everything else is context.
- One line per green item. Leadership does not need the detail, the team already has it in the status page.
- No adjectives without a fact behind them. "Going well" is not an update, the milestone is.

## What it does not do
It does not soften bad news. It orders it: decisions first, risks second, progress last.
