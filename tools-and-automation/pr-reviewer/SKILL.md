---
name: pr-reviewer
description: Review a pull request for secrets, dangerous patterns, and quality issues, before a human approves it. Ships as a GitHub Action that scans every PR and posts the review. Use on any repo where a bad merge can leak a secret or ship unsafe code.
---

# PR reviewer

## Inputs
- A pull request diff, or a set of files to scan. `examples/pr.diff` is a dirty diff, `examples/clean.diff` is a clean one.

## Run
Scan a diff:
```bash
python3 scripts/review.py --diff pr.diff --output review.md
```
Scan files:
```bash
python3 scripts/review.py --files src app --output review.md
```
Exit 0 means APPROVE or COMMENT. Exit 1 means REQUEST CHANGES.

## Output
A review in markdown: a verdict, findings grouped by severity with file, line, and the offending line, and a footer line. The verdict is REQUEST CHANGES when any finding is Critical or High, COMMENT when the worst is Medium, APPROVE when it is clean or Low only.

## Rules
- Secrets are Critical: AWS keys, private keys, GitHub tokens, JWTs, Slack tokens, passwords and API keys assigned in code.
- Dangerous code is High: eval and exec, shell commands, pickle loads, unsafe YAML loads, piping a download to a shell, TLS verification off.
- Changes to the review process itself are High: a PR that touches `.github/workflows/` or the reviewer script gets reviewed by hand.
- The scanner never executes the code it reviews. It reads text.
- The scanner is a first pass, not a full static analysis tool. It catches the common, high-signal issues. A clean review is not proof the code is safe.

## What it does not do
It does not approve anything. It recommends. A human still approves. It does not run tests, and it does not understand what the code is supposed to do.

## Install as a GitHub Action
Copy two files to the repo, on the default branch:
```bash
cp workflow/pr-review.yml .github/workflows/pr-review.yml
cp scripts/review.py .github/scripts/review.py
```
Then turn on branch protection for the default branch and require the "PR Reviewer" check. The workflow runs on `pull_request_target` so it can post comments on PRs from forks. The scanner script comes from the base branch, and only the diff text is read from the PR, so PR code never runs. Actions are pinned to a SHA, and the token has only `contents: read`, `pull-requests: write`, and `issues: write`.

## The schedule
The same workflow also runs on a fixed cron, every day at 02:00 UTC, and scans the whole repo. If it finds anything Critical or High, it opens an issue. Same time every day, same scan, same report format. You can also run it right now from the Actions tab, Run workflow, without waiting for 02:00. On this repo the workflow is already deployed at `.github/workflows/pr-review.yml`, so it is live the moment the repo is uploaded.
