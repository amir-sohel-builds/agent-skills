---
name: retro-pack
description: Assemble a retro pack from the week's facts. Use at the end of a sprint or milestone, when the retro needs to start from what actually happened, not from memory.
---

# Retro pack

## Inputs
- `examples/week.json`: the week's shipped, fixed, and next items, same shape as weekly-flash.
- `examples/workstreams.json`: workstreams with status and blockers, same shape as status-rollup.

## Run
```bash
python3 scripts/retro.py --week week.json --workstreams workstreams.json --output RETRO.md
```

## Output
A retro doc: what shipped, what broke, what is still blocked, a fixed 45-minute agenda, and an empty actions table with owner and due date columns.

## Rules
- The pack is facts only. No opinions, no themes yet. Themes come out of the discussion.
- Every blocked item names its owner. A blocked item with no owner is an action: find the owner.
- Actions leave the retro with an owner and a due date, or they are not actions.
- The agenda is fixed: 15 minutes review, 20 minutes themes, 10 minutes actions.

## What it does not do
It does not run the retro. It assembles the facts so the 45 minutes are spent deciding, not remembering.
