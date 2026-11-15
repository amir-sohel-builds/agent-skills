#!/usr/bin/env python3
"""Render a one-page stakeholder update from a workstreams JSON file."""
import argparse
import json
from datetime import date


def main():
    p = argparse.ArgumentParser(description="Render a stakeholder update from workstreams.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    streams = data.get("workstreams", [])
    red = [w for w in streams if w.get("status") == "red"]
    amber = [w for w in streams if w.get("status") == "amber"]
    green = [w for w in streams if w.get("status") == "green"]
    lines = [f"# Stakeholder update, {date.today().isoformat()}\n"]
    lines.append("## Decisions needed\n")
    if not red:
        lines.append("No decisions needed this week.\n")
    for w in red:
        lines.append(f"- **{w['name']}** ({w.get('owner', 'no owner')})")
        for b in w.get("blockers", []):
            lines.append(f"  - Blocker: {b}")
    lines.append("")
    lines.append("## At risk\n")
    if not amber:
        lines.append("Nothing at risk.\n")
    for w in amber:
        lines.append(f"- **{w['name']}** ({w.get('owner', 'no owner')}): {w.get('milestone', 'no milestone named')}")
        for b in w.get("blockers", []):
            lines.append(f"  - Blocker: {b}")
    lines.append("")
    lines.append("## On track\n")
    if not green:
        lines.append("Nothing on track.\n")
    for w in green:
        lines.append(f"- **{w['name']}**: {w.get('milestone', 'no milestone named')}")
    lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
