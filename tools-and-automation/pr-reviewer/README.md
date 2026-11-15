# PR Reviewer

A GitHub Action that reviews every pull request before a human approves it, and scans the repo itself every night.

## What it does

- On every pull request: scans the diff for secrets, dangerous code, and quality issues, then posts the review as a comment. A REQUEST CHANGES verdict fails the check.
- Every night at 02:00 UTC: scans the whole repo. If it finds anything Critical or High, it opens an issue.
- On demand: run it right now from the Actions tab, Run workflow.

## Files

- `workflow/pr-review.yml`: the workflow. Copy it to `.github/workflows/pr-review.yml`.
- `scripts/review.py`: the scanner. Copy it to `.github/scripts/review.py`.
- `examples/pr.diff`: a dirty diff, for testing. `examples/clean.diff`: a clean one.
- `SKILL.md`: the skill file, same rules, for Claude Code and Cursor.

On this repo the workflow is already deployed at `.github/`, so it is live the moment the repo is uploaded.

## How to see it run

1. Upload the repo to GitHub.
2. Open the Actions tab, select PR Reviewer, click Run workflow. Watch it scan the repo and finish green.
3. Open a test pull request. The bot posts its review as a comment before any human approves.
4. After that, it runs itself every night at 02:00 UTC.

## Security design

- The PR job runs on `pull_request_target` so it can comment on PRs from forks. It never runs code from the PR. The scanner comes from the base branch, and only the diff text is read from the PR.
- Actions are pinned to a SHA, not a tag.
- The token has only `contents: read`, `pull-requests: write`, and `issues: write`.
- The scanner never executes the code it reviews. It reads text. It is a first pass, not a full static analysis tool. A clean review is not proof the code is safe.
