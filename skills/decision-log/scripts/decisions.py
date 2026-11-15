#!/usr/bin/env python3
"""Log decisions with date, context, and decider. Keeps a markdown log."""
import argparse
import json
import os
import sys
from datetime import date


def load(path):
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return {"decisions": data}
        return data
    return {"decisions": []}


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def render(path, data):
    lines = ["# Decisions\n"]
    open_ds = [d for d in data["decisions"] if d.get("status") == "open"]
    closed_ds = [d for d in data["decisions"] if d.get("status") != "open"]
    lines.append("## Open\n")
    if not open_ds:
        lines.append("No open decisions.\n")
    for d in open_ds:
        lines.append(f"- **{d['id']}. {d['title']}** ({d['date']}, decider: {d['decider']})")
        lines.append(f"  - {d['context']}")
    lines.append("")
    lines.append("## Closed\n")
    if not closed_ds:
        lines.append("No closed decisions.\n")
    for d in closed_ds:
        lines.append(f"- **{d['id']}. {d['title']}** ({d['date']}, decider: {d['decider']})")
        lines.append(f"  - {d['context']}")
    lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser(description="Log and list decisions.")
    p.add_argument("--file", default="decisions.json")
    p.add_argument("--output", default="DECISIONS.md")
    sub = p.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("--title", required=True)
    add.add_argument("--context", required=True)
    add.add_argument("--decider", required=True)
    add.add_argument("--date", default=date.today().isoformat())
    add.add_argument("--alternatives", nargs="*", default=[])
    add.add_argument("--reversal", default="")
    sub.add_parser("list")
    close = sub.add_parser("close")
    close.add_argument("--id", type=int, required=True)
    args = p.parse_args()
    data = load(args.file)
    if args.command == "add":
        next_id = max([d["id"] for d in data["decisions"]], default=0) + 1
        data["decisions"].append({
            "id": next_id, "title": args.title, "context": args.context,
            "decider": args.decider, "date": args.date, "status": "open",
            "alternatives": args.alternatives, "reversal": args.reversal,
        })
        save(args.file, data)
        render(args.output, data)
        print(f"Logged decision {next_id}: {args.title}")
    elif args.command == "list":
        open_ds = [d for d in data["decisions"] if d.get("status") == "open"]
        if not open_ds:
            print("No open decisions.")
            return
        for d in open_ds:
            print(f"{d['id']}. {d['title']} ({d['date']}, {d['decider']})")
    elif args.command == "close":
        for d in data["decisions"]:
            if d["id"] == args.id:
                d["status"] = "closed"
                save(args.file, data)
                render(args.output, data)
                print(f"Closed decision {args.id}: {d['title']}")
                return
        print(f"No decision with id {args.id}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
