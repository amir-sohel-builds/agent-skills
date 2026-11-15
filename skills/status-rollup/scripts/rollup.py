#!/usr/bin/env python3
"""Render a one-page status file from a workstreams JSON file."""
import argparse
import json

ORDER = ["red", "amber", "green"]
TITLES = {"red": "Blocked", "amber": "At risk", "green": "On track"}


def main():
    p = argparse.ArgumentParser(description="Render a status page from workstreams.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    lines = ["# Status\n"]
    for status in ORDER:
        items = [w for w in data.get("workstreams", []) if w.get("status") == status]
        if not items:
            continue
        lines.append(f"## {TITLES[status]}\n")
        for w in items:
            lines.append(f"- **{w['name']}** ({w.get('owner', 'no owner')})")
            lines.append(f"  - Next milestone: {w.get('milestone', 'none named')}")
            for b in w.get("blockers", []):
                lines.append(f"  - Blocker: {b}")
        lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
