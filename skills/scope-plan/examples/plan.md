# Plan: Checkout error alerts

## Problem
Checkout errors are found by customers first, not by the team.

## Acceptance criteria
- A user can see checkout errors in one dashboard within one minute of the first failure.
- The system must page the on-call engineer when the error rate passes 1 percent for five minutes.

## Steps
1. List every place checkout errors are logged today.
2. Pick the dashboard and the alert rule.
3. Wire the alert to the on-call rotation.
4. Test it with a synthetic failure.

## Risks
- Alert fatigue if the threshold is too low.
- The dashboard may miss errors from the mobile app.

## Open questions
- Who owns the dashboard after launch? Owner: Priya
- What is the paging rotation? Owner: Sam

## Size
M
