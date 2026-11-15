---
name: dependency-map
description: Build a dependency map from work items. Use when a program has several workstreams and nobody can say what blocks what, or what the critical path is.
---

# Dependency map

## Inputs
- `examples/workstreams.json` shows the shape: each item has an id, a name, an owner, and a `depends_on` list of ids.

## Run
```bash
python3 scripts/depmap.py --input workstreams.json --output DEPENDENCIES.md
```

## Output
A markdown map: items grouped by level, the critical path, and warnings. The script exits 1 when it finds a cycle, and names the cycle.

## Rules
- Every id in a `depends_on` list must exist. An unknown id is a warning, not a silent skip.
- An item nothing depends on and that depends on nothing is an orphan. Orphans get named.
- The critical path is the longest chain of dependencies, counted in items, not guessed.
- A cycle blocks the map. Fix the cycle, then re-run.

## What it does not do
It does not resolve the dependencies. It shows them, in order, so the owners can.
