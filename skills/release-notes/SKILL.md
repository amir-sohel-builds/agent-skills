---
name: release-notes
description: Turn merged work since the last tag into human release notes. Use at release time, when the changelog needs to say what changed and why it matters.
---

# Release notes

## Inputs
- A git repo with tags. The script reads `git log` between two refs.

## Run
```bash
python3 scripts/release_notes.py --from v1.2.0 --to HEAD
```

## Output
Draft notes grouped as Features, Fixes, Docs, Other, from commit prefixes: feat, fix, docs, chore. Edit the draft, do not ship it raw.

## Rules
- Lead with the user-visible change, not the file touched.
- Breaking changes go first, with the action the user must take.
- Drop anything that is not user-visible, like refactors and CI tweaks, unless it changes behavior.
- Never invent a feature from a vague commit message. If the message does not say what changed, leave the item out.

## What it does not do
It does not write the notes. It groups the commits so the human can write them in minutes.
