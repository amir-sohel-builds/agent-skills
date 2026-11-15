---
name: decision-log
description: Log decisions with date, context, and decider. Use whenever a decision is made, so the team can see what was decided, why, and by whom, instead of re-deciding it next month.
---

# Decision log

## Inputs
- A decisions file, `examples/decisions.json` shows the shape. Each decision has an id, a title, context, a decider, a date, and a status of open or closed.

## Run
Log a decision:
```bash
python3 scripts/decisions.py add --title "Ship the new checkout flow" --context "Error rate is flat for two weeks." --decider "Priya" --alternatives "Wait one week" "Ship behind a flag" --reversal "Roll back if the error rate rises above 1 percent for one hour."
```
The `--alternatives` and `--reversal` flags are optional here, but log them when you have them. A decision without them will not pass decision-review.
List what is still open:
```bash
python3 scripts/decisions.py list
```
Close one:
```bash
python3 scripts/decisions.py close --id 2
```
Every command re-renders `DECISIONS.md` next to the JSON file.

## Output
A decision log in markdown: open decisions first, then closed, each with date, decider, and context.

## Rules
- Log it within 24 hours, or it did not happen.
- Context is one or two sentences: what was true when the decision was made.
- The decider is a person, not a team.
- Closed decisions stay in the log. Re-deciding a closed decision starts by reading it.

## What it does not do
It does not make decisions. It makes them findable.
