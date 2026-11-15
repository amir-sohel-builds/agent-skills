---
name: decision-review
description: Grade open decisions for quality: decider, context, alternatives, and reversal criteria. Use when a program keeps re-deciding the same things, or when a decision was made and nobody can say why.
---

# Decision review

## Inputs
- `examples/decisions.json` shows the shape: each decision has an id, a title, context, a decider, a date, a status, a list of alternatives considered, and reversal criteria.

## Run
```bash
python3 scripts/review.py --input decisions.json --output REVIEW.md
```

## Output
A review: complete decisions, incomplete decisions with exactly what is missing, and closed decisions. The script exits 1 when any open decision is incomplete.

## Rules
- A decision with no alternatives is a guess with a signature. Two alternatives is the minimum.
- Reversal criteria are set when the decision is made, not when it goes wrong.
- The decider is a person. A committee is not a decider.
- Context is what was true when the decision was made, in one or two sentences.

## What it does not do
It does not judge whether the decision was right. It checks whether it was made well.
