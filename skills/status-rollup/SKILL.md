---
name: status-rollup
description: Roll up workstreams into one honest status page. Use when status is scattered across repos and tickets and the team needs one page with blockers named, no manual chasing.
---

# Status rollup

## Inputs
- `examples/workstreams.json` shows the shape: each workstream has a name, an owner, a status of green, amber, or red, a next milestone, and blockers.

## Run
```bash
python3 scripts/rollup.py --input workstreams.json --output STATUS.md
```

## Output
A one-page status file: blocked, at risk, and on track sections, each workstream with owner, milestone, and blockers.

## Rules
- A workstream with no owner is red, not green. The script does not decide this, you do, when you write the file.
- A blocker with no owner is not a blocker, it is a wish. Name the owner.
- Never write "on track" for work with no milestone. Say what the milestone is.

## What it does not do
It does not gather the status. It renders the status you collected, in one place, in order.
