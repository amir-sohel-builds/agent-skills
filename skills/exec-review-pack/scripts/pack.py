#!/usr/bin/env python3
"""Build a one-page exec review pack from status, risks, and decisions."""
import argparse
import json
from datetime import date


def main():
    p = argparse.ArgumentParser(description="Build a one-page exec review pack.")
    p.add_argument("--workstreams", required=True)
    p.add_argument("--risks", required=True)
    p.add_argument("--decisions", required=True)
    p.add_argument("--since", default=None)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    def load_list(path, key):
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get(key, [])

    def blocker_text(b):
        if isinstance(b, dict):
            text = b.get("text", "")
            owner = b.get("owner")
            return f"{text} (owner: {owner})" if owner else text
        return b

    streams = load_list(args.workstreams, "workstreams")
    risks = load_list(args.risks, "risks")
    decisions = load_list(args.decisions, "decisions")
    red = [w for w in streams if w.get("status") == "red"]
    amber = [w for w in streams if w.get("status") == "amber"]
    green = [w for w in streams if w.get("status") == "green"]
    top = sorted([r for r in risks if r.get("status") == "open"
                  and r.get("likelihood", 0) * r.get("impact", 0) >= 15],
                 key=lambda r: r["likelihood"] * r["impact"], reverse=True)
    recent = [d for d in decisions if d.get("status") == "open"
              and (not args.since or d.get("date", "") >= args.since)]
    lines = [f"# Exec review, {date.today().isoformat()}\n"]
    lines.append("## Decisions needed\n")
    if not red and not top:
        lines.append("No decisions needed.\n")
    for w in red:
        lines.append(f"- **{w['name']}** ({w.get('owner', 'no owner')}): {', '.join(blocker_text(b) for b in w.get('blockers', [])) or 'no blocker named'}")
    for r in top:
        lines.append(f"- Risk **{r['id']}** {r['title']} (score {r['likelihood'] * r['impact']}, owner: {r.get('owner') or 'NONE'})")
    lines.append("")
    lines.append(f"## Decisions since {args.since}\n" if args.since else "## Open decisions\n")
    if not recent:
        lines.append("None.\n")
    for d in recent:
        lines.append(f"- **{d['title']}** ({d['date']}, decider: {d.get('decider') or 'NONE'})")
    lines.append("")
    lines.append("## Top risks\n")
    if not top:
        lines.append("None.\n")
    for r in top:
        lines.append(f"- **{r['id']}** {r['title']} (score {r['likelihood'] * r['impact']})")
    lines.append("")
    lines.append("## On track\n")
    if green:
        lines.append(f"{len(green)} of {len(streams)} workstreams on track: " + ", ".join(w["name"] for w in green) + ".")
    else:
        lines.append("Nothing on track.")
    lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
