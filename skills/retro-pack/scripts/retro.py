#!/usr/bin/env python3
"""Assemble a retro pack from the week's facts: shipped, broken, still blocked."""
import argparse
import json


def main():
    p = argparse.ArgumentParser(description="Assemble a retro pack from the week's facts.")
    p.add_argument("--week", required=True)
    p.add_argument("--workstreams", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.week) as f:
        week = json.load(f)
    with open(args.workstreams) as f:
        wsdata = json.load(f)
    if isinstance(wsdata, list):
        wsdata = {"workstreams": wsdata}
    streams = wsdata.get("workstreams", [])
    blocked = [w for w in streams if w.get("status") in ("red", "amber")]
    lines = [f"# Retro, {week.get('week', 'this week')}\n"]
    lines.append("## What shipped\n")
    for item in week.get("shipped", []):
        lines.append(f"- {item['text']}")
    if not week.get("shipped"):
        lines.append("- Nothing shipped.")
    lines.append("")
    lines.append("## What broke\n")
    for item in week.get("fixed", []):
        lines.append(f"- {item['text']}")
    if not week.get("fixed"):
        lines.append("- Nothing broke.")
    lines.append("")
    lines.append("## Still blocked\n")
    if not blocked:
        lines.append("Nothing blocked.\n")
    for w in blocked:
        lines.append(f"- **{w['name']}** ({w.get('owner', 'no owner')}, {w.get('status')})")
        for b in w.get("blockers", []):
            if isinstance(b, dict):
                text = b.get("text", "")
                owner = b.get("owner")
                b = f"{text} (owner: {owner})" if owner else text
            lines.append(f"  - {b}")
    lines.append("")
    lines.append("## Agenda (45 minutes)\n")
    lines.append("- 15 min: review what shipped and what broke")
    lines.append("- 20 min: themes, what to keep, what to change")
    lines.append("- 10 min: actions, each with an owner and a due date")
    lines.append("")
    lines.append("## Actions\n")
    lines.append("| Action | Owner | Due |")
    lines.append("| --- | --- | --- |")
    lines.append("|  |  |  |")
    lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
