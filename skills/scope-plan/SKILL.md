---
name: scope-plan
description: Turn a vague request into a scoped plan, then check the plan is complete. Use before work starts, when the ask is unclear and the team needs acceptance criteria, steps, risks, and owners.
---

# Scope plan

## Inputs
- A request in plain text, `examples/request.md` shows the shape.
- The template, `templates/plan.md`. Copy it, do not write a plan from a blank page.

## Run
Write the plan from the template, then check it:

```bash
python3 scripts/plan_check.py --plan plan.md
```

## Output
A plan file with six sections: Problem, Acceptance criteria, Steps, Risks, Open questions, Size. The checker prints PASS or FAIL for each section and exits 1 when anything fails.

## Rules
- The problem is one sentence. If it takes two, the ask is two projects.
- Every acceptance criterion is a check, starting with "A user can" or "The system must".
- Every open question names an owner, written as "Owner: Name".
- Size is one letter: S, M, or L. No hours, no points, no fake precision.
- A plan that fails the check is a draft, not a plan.

## What it does not do
It does not decide whether the work is worth doing. It does not estimate. It checks that the plan is complete enough to start.
