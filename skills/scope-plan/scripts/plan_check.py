#!/usr/bin/env python3
"""Check a plan file for completeness. Exits 1 when any check fails."""
import argparse
import re
import sys

REQUIRED = ["Problem", "Acceptance criteria", "Steps", "Risks", "Open questions", "Size"]


def sections(text):
    out = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            current = m.group(1).strip()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def bullets(body):
    return [l[2:].strip() for l in body.splitlines() if l.startswith("- ") and l[2:].strip()]


def main():
    p = argparse.ArgumentParser(description="Check a plan file for completeness.")
    p.add_argument("--plan", required=True)
    args = p.parse_args()
    with open(args.plan) as f:
        secs = sections(f.read())
    checks = []
    for name in REQUIRED:
        checks.append((f"section present: {name}", name in secs and bool(secs[name])))
    criteria = bullets(secs.get("Acceptance criteria", ""))
    checks.append(("acceptance criteria: at least 1", len(criteria) >= 1))
    checks.append(("acceptance criteria: each starts with a check",
                   all(c.startswith(("A user can", "The system must")) for c in criteria)))
    steps = [l for l in secs.get("Steps", "").splitlines()
             if re.match(r"^(\d+\.|-) ", l.strip())]
    checks.append(("steps: at least 1", len(steps) >= 1))
    checks.append(("risks: at least 1", len(bullets(secs.get("Risks", ""))) >= 1))
    questions = bullets(secs.get("Open questions", ""))
    checks.append(("open questions: every one names an owner",
                   all("Owner:" in q for q in questions)))
    checks.append(("size: S, M, or L", secs.get("Size", "").strip() in ("S", "M", "L")))
    failed = 0
    print("# Plan check\n")
    for name, ok in checks:
        print(f"- [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            failed += 1
    print(f"\nFailed: {failed}/{len(checks)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
