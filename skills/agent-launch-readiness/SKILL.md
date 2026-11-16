---
name: agent-launch-readiness
description: Check an agent spec before it goes live. Use when a team wants an agent in production and needs a GO or NO-GO with the gaps named, not a feeling.
---

# Agent launch readiness

## Inputs
- An agent spec file. `templates/agent-spec.json` is the blank one. It records the owner, approved sources, eval results, rollback, cost cap, actions, permissions, logging, and privacy review.

## Run
```bash
python3 scripts/launch_check.py --input agent-spec.json
```

## Output
A verdict: GO or NO-GO. Every blocking gap is named with the reason. Warnings are listed separately and never block. The exit code is 0 for GO and 1 for NO-GO.

## Rules
- GO only when all twelve checks pass: owner, approved sources, refuses without a source, eval suite, eval pass rate at or above the threshold, one-step rollback, versioned prompts, monthly cost cap, human approval on every write action, runs with the caller's permissions, logs and traces on, privacy review when personal data is handled.
- A missing field counts as failing. "Not answered" is not a yes.
- The eval threshold defaults to 90 when the spec does not set one.
- A pass rate within 3 points of the threshold is a warning, not a block.
- A NO-GO is not a failure. It is the check doing its job.

## What it does not do
It does not judge whether the sources are the right ones, whether the evals are any good, or whether the cost cap is sensible. It checks that each exists and that the numbers clear the bar the team set. People make those calls.
