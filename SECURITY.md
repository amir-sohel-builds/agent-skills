# Security

## Reporting

If you find a security issue in this repo, open a private security advisory on GitHub. Do not open a public issue with exploit details.

## What this repo contains

- Python scripts using only the standard library. No dependencies, so no supply chain to attack.
- No secrets, no keys, no tokens, no credentials anywhere in the repo.
- No network calls in any skill script. The only network operation is `git clone` of this repo's own hardcoded URL in `install.sh`.
- The docs site has no external scripts and no tracking. Its only JavaScript is the copy button.

## Audit, 2026-11-14

Method: read every script and `install.sh`, searched for dangerous patterns (eval, exec, shell commands, pickle, unsafe YAML, pipe to shell, TLS off), searched for secret-looking strings, and ran the repo's own pr-reviewer scanner over the whole repo.

Result: no Critical or High findings.

Two Low findings, both fixed the same day:

1. `install.sh` had a comment suggesting `curl ... | bash` to run it. Removed. The install path is: clone the repo, read the script, then run it.
2. `install.sh --only` accepted any string, so `--only ../docs` could point outside the skills folder. It now accepts only lowercase letters, digits, and hyphens, and still requires the skill folder to exist.

Notes, not findings:

- The installer deletes an existing skill folder with the same name before copying the new one. That is how updates work. It only ever touches `~/.claude/skills/<name>` and `~/.cursor/skills/<name>`.
- `release-notes` runs `git log` through `subprocess` with list arguments and no shell. `run_evals.py` runs only its own hardcoded command list.

## The security gate

The evals include a security check. `python3 evals/run_evals.py` runs the pr-reviewer scanner over the whole repo and fails on any Critical or High finding. A skill that fails the security gate is not shipped.

The repo also scans itself. The PR Reviewer workflow is deployed at `.github/workflows/pr-review.yml` and runs on a fixed cron, every day at 02:00 UTC, scanning the whole repo. If it finds anything Critical or High, it opens an issue. You can also run it on demand from the Actions tab, Run workflow.

To scan any repo's pull requests, use the pr-reviewer skill. It ships as a GitHub Action. See `tools-and-automation/pr-reviewer/SKILL.md`.
