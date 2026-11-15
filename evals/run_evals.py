#!/usr/bin/env python3
"""Evals for agent-skills. Runs every skill against its examples and checks the outputs.

Usage: python3 evals/run_evals.py
Exits 1 when any eval fails.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNED = ["forge", "mobius", "sleek", "dont-hallucinate", "79+", "17,000", "wbd",
          "warner", "incident", "triage", "vibe-coded", "eval-gate"]

CASES = [
    {"name": "scope-plan", "cmd": ["python3", "skills/scope-plan/scripts/plan_check.py", "--plan", "skills/scope-plan/examples/plan.md"], "exit": 0, "contains": ["Failed: 0/12"]},
    {"name": "dependency-map", "cmd": ["python3", "skills/dependency-map/scripts/depmap.py", "--input", "skills/dependency-map/examples/workstreams.json"], "exit": 0, "contains": ["Critical path"]},
    {"name": "dependency-map broken", "cmd": ["python3", "skills/dependency-map/scripts/depmap.py", "--input", "skills/dependency-map/examples/broken.json"], "exit": 1, "contains": ["Cycles"]},
    {"name": "capacity-plan", "cmd": ["python3", "skills/capacity-plan/scripts/capacity.py", "--input", "skills/capacity-plan/examples/capacity.json"], "exit": 1, "contains": ["OVER"]},
    {"name": "risk-register", "cmd": ["python3", "skills/risk-register/scripts/risks.py", "--input", "skills/risk-register/examples/risks.json"], "exit": 0, "contains": ["R1", "score 20"]},
    {"name": "status-rollup", "cmd": ["python3", "skills/status-rollup/scripts/rollup.py", "--input", "skills/status-rollup/examples/workstreams.json"], "exit": 0, "contains": ["Blocked"]},
    {"name": "stakeholder-update", "cmd": ["python3", "skills/stakeholder-update/scripts/update.py", "--input", "skills/stakeholder-update/examples/workstreams.json"], "exit": 0, "contains": ["Decisions needed"]},
    {"name": "decision-log", "cmd": ["python3", "skills/decision-log/scripts/decisions.py", "--file", "skills/decision-log/examples/decisions.json", "list"], "exit": 0, "contains": ["Ship the new checkout flow"]},
    {"name": "launch-readiness", "cmd": ["python3", "skills/launch-readiness/scripts/readiness.py", "--input", "skills/launch-readiness/examples/checklist.json"], "exit": 1, "contains": ["NO-GO"]},
    {"name": "weekly-flash", "cmd": ["python3", "skills/weekly-flash/scripts/flash.py", "--input", "skills/weekly-flash/examples/week.json"], "exit": 0, "contains": ["Weekly flash"]},
    {"name": "report-trust-check", "cmd": ["python3", "skills/report-trust-check/scripts/check_csv.py", "--file", "skills/report-trust-check/examples/data.csv", "--date-col", "updated_at", "--stale-days", "7", "--key-col", "id"], "exit": 0, "contains": ["duplicate key"]},
    {"name": "retro-pack", "cmd": ["python3", "skills/retro-pack/scripts/retro.py", "--week", "skills/retro-pack/examples/week.json", "--workstreams", "skills/retro-pack/examples/workstreams.json"], "exit": 0, "contains": ["Retro"]},
    {"name": "quarterly-plan", "cmd": ["python3", "skills/quarterly-plan/scripts/quarter.py", "--teams", "skills/quarterly-plan/examples/teams.json", "--initiatives", "skills/quarterly-plan/examples/initiatives.json"], "exit": 1, "contains": ["OVER", "Ordering violations"]},
    {"name": "decision-review", "cmd": ["python3", "skills/decision-review/scripts/review.py", "--input", "skills/decision-review/examples/decisions.json"], "exit": 1, "contains": ["Incomplete"]},
    {"name": "exec-review-pack", "cmd": ["python3", "skills/exec-review-pack/scripts/pack.py", "--workstreams", "skills/exec-review-pack/examples/workstreams.json", "--risks", "skills/exec-review-pack/examples/risks.json", "--decisions", "skills/exec-review-pack/examples/decisions.json", "--since", "2026-11-01"], "exit": 0, "contains": ["Exec review", "Decisions needed"]},
    {"name": "pr-reviewer dirty", "cmd": ["python3", "tools-and-automation/pr-reviewer/scripts/review.py", "--diff", "tools-and-automation/pr-reviewer/examples/pr.diff"], "exit": 1, "contains": ["REQUEST CHANGES", "Reviewed by PR Reviewer bot"]},
    {"name": "pr-reviewer clean", "cmd": ["python3", "tools-and-automation/pr-reviewer/scripts/review.py", "--diff", "tools-and-automation/pr-reviewer/examples/clean.diff"], "exit": 0, "contains": ["APPROVE", "Reviewed by PR Reviewer bot"]},
    {"name": "security gate", "cmd": ["python3", "tools-and-automation/pr-reviewer/scripts/review.py", "--files", "skills", "tools-and-automation", ".github", "README.md", "install.sh", "docs", "evals", "--exclude", "tools-and-automation/pr-reviewer/scripts/review.py", "--exclude", "tools-and-automation/pr-reviewer/examples", "--exclude", ".github/scripts/review.py"], "exit": 0, "contains": ["0 critical, 0 high"]},
]


def run(cmd, cwd=ROOT, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def main():
    failures = 0
    for case in CASES:
        code, out = run(case["cmd"])
        ok = code == case["exit"] and all(s in out for s in case["contains"])
        print(f"[{'PASS' if ok else 'FAIL'}] {case['name']}")
        if not ok:
            failures += 1
            print(f"  expected exit {case['exit']}, got {code}; missing: {[s for s in case['contains'] if s not in out]}")
    # Release notes needs a temp git repo.
    with tempfile.TemporaryDirectory() as d:
        run(["git", "init", "-q"], cwd=d)
        run(["git", "config", "user.email", "t@t"], cwd=d)
        run(["git", "config", "user.name", "t"], cwd=d)
        run(["git", "commit", "-q", "--allow-empty", "-m", "feat: add checkout"], cwd=d)
        run(["git", "tag", "v1.2.0"], cwd=d)
        run(["git", "commit", "-q", "--allow-empty", "-m", "fix: retry on timeout"], cwd=d)
        code, out = run(["python3", os.path.join(ROOT, "skills/release-notes/scripts/release_notes.py"), "--from", "v1.2.0", "--to", "HEAD"], cwd=d)
        ok = code == 0 and "retry on timeout" in out
        print(f"[{'PASS' if ok else 'FAIL'}] release-notes")
        if not ok:
            failures += 1
    # Deployed copies match the canonical tool files.
    pairs = [
        ("tools-and-automation/pr-reviewer/workflow/pr-review.yml", ".github/workflows/pr-review.yml"),
        ("tools-and-automation/pr-reviewer/scripts/review.py", ".github/scripts/review.py"),
    ]
    match = True
    for src, dst in pairs:
        try:
            with open(os.path.join(ROOT, src)) as f:
                a = f.read()
            with open(os.path.join(ROOT, dst)) as f:
                b = f.read()
            if a != b:
                match = False
                print(f"  {dst} differs from {src}")
        except OSError as e:
            match = False
            print(f"  {e}")
    print(f"[{'PASS' if match else 'FAIL'}] deployed copies match")
    if not match:
        failures += 1
    # Workflow has the PR trigger, the cron schedule, and the manual trigger.
    wf = open(os.path.join(ROOT, "tools-and-automation/pr-reviewer/workflow/pr-review.yml")).read()
    triggers = all(s in wf for s in ("pull_request_target", "schedule", "workflow_dispatch", 'cron: "0 2 * * *"'))
    print(f"[{'PASS' if triggers else 'FAIL'}] workflow triggers (PR, cron, manual)")
    if not triggers:
        failures += 1
    # Workflow YAML parses, with both jobs. A bad workflow is a silent failure on GitHub.
    try:
        import yaml
        parsed = yaml.safe_load(open(os.path.join(ROOT, "tools-and-automation/pr-reviewer/workflow/pr-review.yml")))
        yaml_ok = set(parsed.get("jobs", {}).keys()) == {"review", "nightly"}
        print(f"[{'PASS' if yaml_ok else 'FAIL'}] workflow yaml parses (jobs: review, nightly)")
        if not yaml_ok:
            failures += 1
    except ImportError:
        print("[SKIP] workflow yaml parse (PyYAML not installed)")
    # Installer installs every skill.
    with tempfile.TemporaryDirectory() as home:
        os.makedirs(os.path.join(home, ".cursor"), exist_ok=True)
        env = dict(os.environ, HOME=home)
        code, out = run(["bash", "install.sh"], cwd=ROOT, env=env)
        expected = 0
        for folder in ("skills", "tools-and-automation"):
            d = os.path.join(ROOT, folder)
            expected += len([x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))])
        n_claude = len(os.listdir(os.path.join(home, ".claude", "skills"))) if os.path.isdir(os.path.join(home, ".claude", "skills")) else 0
        n_cursor = len(os.listdir(os.path.join(home, ".cursor", "skills"))) if os.path.isdir(os.path.join(home, ".cursor", "skills")) else 0
        ok = code == 0 and n_claude == expected and n_cursor == expected
        print(f"[{'PASS' if ok else 'FAIL'}] installer ({n_claude} claude, {n_cursor} cursor, expected {expected})")
        if not ok:
            failures += 1
    # No company info anywhere in the repo. The evals folder itself holds the banned list, so skip it.
    hits = []
    for dirpath, dirnames, files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "evals")]
        for fn in files:
            if fn.endswith((".zip", ".pyc")):
                continue
            path = os.path.join(dirpath, fn)
            try:
                text = open(path, errors="ignore").read().lower()
            except OSError:
                continue
            for term in BANNED:
                if term in text:
                    hits.append(f"{os.path.relpath(path, ROOT)}: {term}")
    ok = not hits
    print(f"[{'PASS' if ok else 'FAIL'}] no company info")
    if hits:
        failures += 1
        for h in hits[:10]:
            print(f"  {h}")
    print(f"\nFailed: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
