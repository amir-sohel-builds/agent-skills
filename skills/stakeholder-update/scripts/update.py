#!/usr/bin/env python3
"""Render a one-page stakeholder update from a workstreams JSON file."""
import argparse
import json
from datetime import date


def blocker_text(b):
    if isinstance(b, dict):
        text = b.get("text", "")
        owner = b.get("owner")
        return f"{text} (owner: {owner})" if owner else text
    return b


def milestone(w):
    return w.get("milestone") or w.get("next_milestone") or "no milestone named"


def main():
    p = argparse.ArgumentParser(description="Render a stakeholder update from workstreams.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    if isinstance(data, list):
        data = {"workstreams": data}
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
            lines.append(f"  - Blocker: {blocker_text(b)}")
    lines.append("")
    lines.append("## At risk\n")
    if not amber:
        lines.append("Nothing at risk.\n")
    for w in amber:
        lines.append(f"- **{w['name']}** ({w.get('owner', 'no owner')}): {milestone(w)}")
        for b in w.get("blockers", []):
            lines.append(f"  - Blocker: {blocker_text(b)}")
    lines.append("")
    lines.append("## On track\n")
    if not green:
        lines.append("Nothing on track.\n")
    for w in green:
        lines.append(f"- **{w['name']}**: {milestone(w)}")
    lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
