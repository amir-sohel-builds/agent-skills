---
name: launch-readiness
description: Evaluate a launch checklist. Use before a launch, when the team needs a GO or NO-GO call with reasons, not a feeling.
---

# Launch readiness

## Inputs
- A checklist file. `templates/checklist.json` is the blank one. Each item has an id, a question, a status of yes, no, or na, an owner, and evidence.

## Run
```bash
python3 scripts/readiness.py --input checklist.json
```

## Output
A verdict: GO or NO-GO. Every NO-GO reason is named with its owner. Items marked na are listed separately.

## Rules
- GO only when every required item is yes. Required means every item not marked na.
- An item with no status counts as no, with the reason "not answered".
- Evidence is a link, a run id, or a file. "Trust me" is not evidence.
- A NO-GO is not a failure. It is the checklist doing its job.

## What it does not do
It does not decide what the checklist should contain. The team writes the items, the tool evaluates them.
