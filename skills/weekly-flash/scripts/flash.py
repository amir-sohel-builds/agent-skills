#!/usr/bin/env python3
"""Render a one-page weekly flash report from a week JSON file."""
import argparse
import json
from datetime import date


def section(lines, title, items):
    if not items:
        return
    lines.append(f"## {title}\n")
    for item in items:
        link = f" ({item['link']})" if item.get("link") else ""
        lines.append(f"- {item['text']}{link}")
    lines.append("")


def main():
    p = argparse.ArgumentParser(description="Render a weekly flash report.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    lines = [f"# Weekly flash, {data.get('week', date.today().isoformat())}\n"]
    section(lines, "Shipped", data.get("shipped", []))
    section(lines, "Fixed", data.get("fixed", []))
    section(lines, "Next", data.get("next", []))
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
