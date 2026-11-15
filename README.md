# agent-skills

A TPM suite. Sixteen deterministic tools for planning, running, and reporting programs. No slop.

I am Amir Sohel, a Staff Technical Program Manager. These are the tools I use to run programs, built so any TPM can use them at any company. Each skill does one job, takes a real input, and produces a real artifact. No advice dressed as a tool.

## The rule

Every skill ships a script. If it cannot be run, it is not in this repo. A skill has exact inputs, one exact command, and one exact output. What needs human judgment is named as human judgment, not hidden inside the tool.

## Install

```bash
git clone https://github.com/amir-sohel-builds/agent-skills.git
cd agent-skills
bash install.sh
```

That copies every skill into `~/.claude/skills` and, if it exists, `~/.cursor/skills`. To install one skill only:

```bash
bash install.sh --only risk-register
```

## The skills

### Plan it

| Skill | What it does |
| --- | --- |
| scope-plan | Turns a vague request into a scoped plan, then checks the plan is complete. |
| dependency-map | Builds a dependency map from work items. Finds cycles, orphans, and the critical path. |
| capacity-plan | Matches committed work against team capacity, by person and by week. Flags over-allocation. |
| risk-register | Scores risks by likelihood times impact, sorts them, and flags the top ones. |

### Run it

| Skill | What it does |
| --- | --- |
| status-rollup | Rolls up workstreams into one honest status page, blockers named. |
| stakeholder-update | Turns the same status file into a one-page exec update. Risks first. |
| decision-log | Logs decisions with date, context, and decider. Lists what is still open. |
| launch-readiness | Evaluates a launch checklist. GO only when every required item is yes. |

### Prove it

| Skill | What it does |
| --- | --- |
| weekly-flash | Turns the week's shipped work into a one-page flash report. |
| release-notes | Turns merged work since the last tag into human release notes. |
| report-trust-check | Audits the data behind a report: stale rows, missing values, duplicates. |
| retro-pack | Assembles a retro pack from the week's facts: shipped, broken, still blocked. |
| pr-reviewer | Reviews a pull request for secrets, dangerous patterns, and quality issues, before a human approves it. Ships as a GitHub Action. Lives in `tools-and-automation/`. |

### Lead it

| Skill | What it does |
| --- | --- |
| quarterly-plan | Builds a quarter plan across teams: load against capacity, cross-team dependencies, ordering checks. |
| decision-review | Grades open decisions for quality: decider, context, alternatives, reversal criteria. |
| exec-review-pack | Builds a one-page exec review pack from status, risks, and decisions. |

## Evals

Every skill is tested against its examples. Run the evals with:

```bash
python3 evals/run_evals.py
```

It runs all sixteen skills, checks their outputs, tests the installer, and checks the whole repo for company info. It exits 1 when anything fails. A skill that fails its eval is not shipped.

## Security

Audited 2026-11-14, see `SECURITY.md`. No Critical or High findings. Two Low findings fixed the same day: `install.sh` no longer suggests piping it from the internet, and `--only` now accepts only real skill names, so it cannot point outside the skills folder. The evals include a security gate: the pr-reviewer scanner runs over the whole repo and fails on any Critical or High finding. To scan pull requests in any repo, use the pr-reviewer skill, which ships as a GitHub Action.

## Tools and automation

Tools live in `tools-and-automation/`. The first one is pr-reviewer, a GitHub Action that reviews every pull request and scans the repo itself every night at 02:00 UTC. It is already deployed in this repo at `.github/workflows/pr-review.yml`, so it is live the moment the repo is uploaded. To see it run right away, open the Actions tab, select PR Reviewer, and click Run workflow. Upload the tools folder first, watch it run, then the rest of the repo.

## How a skill works

Each skill lives in `skills/<name>/`, or in `tools-and-automation/<name>/` for tools, and has a `SKILL.md` file in a fixed shape: Inputs, Run, Output, Rules, and What it does not do. The script lives under `scripts/` and the worked example under `examples/`. The script is the skill. The SKILL.md tells you how to run it and how to read what comes out.

## Use with Claude Code

Claude Code picks up skills from `~/.claude/skills`. After installing, just describe the job, for example "roll up this week's status from workstreams.json", and the matching skill loads. The same files work in Cursor from `~/.cursor/skills`.

## Contributing

Small is a feature. A new skill should do one job, ship a script, and include a worked example. No advice-only skills. Open a PR with the skill folder and a one-line entry in the table above.

## License

MIT. Use them, fork them, make them yours.

---

About me: I'm Amir Sohel, Staff Technical Program Manager. I run programs with these tools, and I write about building and automating at [amir-sohel-builds.github.io](https://amir-sohel-builds.github.io).
