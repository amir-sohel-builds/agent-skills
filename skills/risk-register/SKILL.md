---
name: risk-register
description: Score risks by likelihood times impact, sort them, and flag the top ones. Use when a program needs its risks written down, ranked, and owned, not carried in someone's head.
---

# Risk register

## Inputs
- `examples/risks.json` shows the shape: each risk has an id, a title, likelihood 1 to 5, impact 1 to 5, an owner, a mitigation, and a status of open or closed.

## Run
```bash
python3 scripts/risks.py --input risks.json --output RISKS.md
```

## Output
A register sorted by score, highest first, with a top risks section for anything scoring 15 or more. Risks with no owner or no mitigation are flagged.

## Rules
- Score is likelihood times impact. Both are 1 to 5, set by the owner, not by the tool.
- A risk with no owner is not a risk, it is a hope. It gets flagged.
- A top risk with no mitigation is the first thing on the agenda.
- Closed risks stay in the register, at the bottom. Deleting them deletes the lesson.

## What it does not do
It does not judge likelihood or impact. The owner sets both numbers, the tool does the arithmetic.
