#!/usr/bin/env python3
"""Draft release notes from git log between two refs."""
import argparse
import re
import subprocess
from collections import defaultdict

GROUPS = [
    ("Features", ["feat"]),
    ("Fixes", ["fix"]),
    ("Docs", ["docs"]),
    ("Other", ["chore", "refactor", "test", "ci"]),
]


def git_log(from_ref, to_ref):
    out = subprocess.run(
        ["git", "log", f"{from_ref}..{to_ref}", "--oneline"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.splitlines()


def main():
    p = argparse.ArgumentParser(description="Draft release notes from git log.")
    p.add_argument("--from", dest="from_ref", required=True)
    p.add_argument("--to", dest="to_ref", default="HEAD")
    args = p.parse_args()
    grouped = defaultdict(list)
    for line in git_log(args.from_ref, args.to_ref):
        m = re.match(r"^[0-9a-f]+ (\w+)(?:\([^)]*\))?: (.*)$", line)
        if not m:
            grouped["Other"].append(line)
            continue
        kind, msg = m.group(1).lower(), m.group(2)
        placed = False
        for title, kinds in GROUPS:
            if kind in kinds:
                grouped[title].append(msg)
                placed = True
                break
        if not placed:
            grouped["Other"].append(msg)
    print("# Release notes (draft)\n")
    for title, _ in GROUPS:
        items = grouped.get(title, [])
        if not items:
            continue
        print(f"## {title}\n")
        for item in items:
            print(f"- {item}")
        print()


if __name__ == "__main__":
    main()
