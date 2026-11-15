#!/usr/bin/env python3
"""Grade open decisions: decider, context, alternatives, reversal criteria."""
import argparse
import json
import sys

CHECKS = [
    ("decider", lambda d: bool(d.get("decider"))),
    ("context", lambda d: len((d.get("context") or "").strip()) >= 10),
    ("alternatives", lambda d: len(d.get("alternatives") or []) >= 2),
    ("reversal criteria", lambda d: bool((d.get("reversal") or "").strip())),
]


def main():
    p = argparse.ArgumentParser(description="Grade open decisions for quality.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    open_ds = [d for d in data.get("decisions", []) if d.get("status") == "open"]
    closed_ds = [d for d in data.get("decisions", []) if d.get("status") != "open"]
    complete, incomplete = [], []
    for d in open_ds:
        missing = [name for name, fn in CHECKS if not fn(d)]
        (complete if not missing else incomplete).append((d, missing))
    lines = ["# Decision review\n"]
    lines.append(f"Open decisions: {len(open_ds)}. Complete: {len(complete)}. Incomplete: {len(incomplete)}.\n")
    lines.append("## Complete\n")
    if not complete:
        lines.append("None.\n")
    for d, _ in complete:
        lines.append(f"- **{d['id']}. {d['title']}** ({d['date']}, decider: {d['decider']})")
    lines.append("")
    lines.append("## Incomplete\n")
    if not incomplete:
        lines.append("None.\n")
    for d, missing in incomplete:
        lines.append(f"- **{d['id']}. {d['title']}** ({d['date']})")
        lines.append(f"  - Missing: {', '.join(missing)}")
    lines.append("")
    if closed_ds:
        lines.append("## Closed\n")
        for d in closed_ds:
            lines.append(f"- {d['id']}. {d['title']} ({d['date']})")
        lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)
    sys.exit(1 if incomplete else 0)


if __name__ == "__main__":
    main()
