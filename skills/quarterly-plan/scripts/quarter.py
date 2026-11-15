#!/usr/bin/env python3
"""Build a quarter plan: multi-team load, cross-team deps, ordering checks."""
import argparse
import json
import sys
from collections import defaultdict


def main():
    p = argparse.ArgumentParser(description="Build a quarter plan from teams and initiatives.")
    p.add_argument("--teams", required=True)
    p.add_argument("--initiatives", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.teams) as f:
        tdata = json.load(f)
    if isinstance(tdata, list):
        tdata = {"teams": tdata}
    teams = {t["name"]: t for t in tdata.get("teams", [])}
    for name, t in teams.items():
        if "hours_per_week" not in t:
            print(f"Team {name} has no hours_per_week.", file=sys.stderr)
            sys.exit(2)
    with open(args.initiatives) as f:
        idata = json.load(f)
    if isinstance(idata, list):
        idata = {"initiatives": idata}
    inits = {i["id"]: i for i in idata.get("initiatives", [])}
    def headcount(t):
        p = t.get("people", 0)
        return p if isinstance(p, int) else len(p)

    def title(i):
        return i.get("title") or i.get("name") or i["id"]

    load = defaultdict(lambda: defaultdict(int))
    for i in inits.values():
        load[i["week"]][i["team"]] += i["hours"]
    over = []
    lines = ["# Quarter plan\n"]
    for week in sorted(load):
        lines.append(f"## Week {week}\n")
        lines.append("| Team | Capacity | Load | Status |")
        lines.append("| --- | ---: | ---: | --- |")
        for team in sorted(teams):
            cap = headcount(teams[team]) * teams[team]["hours_per_week"]
            used = load[week].get(team, 0)
            status = "OVER" if used > cap else ("UNDER" if used < cap / 2 else "OK")
            if used > cap:
                over.append((week, team, used, cap))
            lines.append(f"| {team} | {cap} | {used} | {status} |")
        lines.append("")
    cross = []
    violations = []
    for i in inits.values():
        for dep in i.get("depends_on", []):
            if dep not in inits:
                continue
            d = inits[dep]
            if d["team"] != i["team"]:
                cross.append((i, d))
            if d["week"] > i["week"]:
                violations.append((i, d))
    lines.append("## Cross-team dependencies\n")
    if not cross:
        lines.append("None.\n")
    for i, d in cross:
        lines.append(f"- **{i['id']}** {title(i)} ({i['team']}) depends on **{d['id']}** {title(d)} ({d['team']})")
    lines.append("")
    lines.append("## Ordering violations\n")
    if not violations:
        lines.append("None.\n")
    for i, d in violations:
        lines.append(f"- **{i['id']}** {title(i)} is scheduled {i['week']}, but its dependency **{d['id']}** {title(d)} is scheduled {d['week']}")
    lines.append("")
    total_load = sum(i["hours"] for i in inits.values())
    total_cap = sum(headcount(t) * t["hours_per_week"] for t in teams.values()) * len(load)
    lines.append("## Summary\n")
    lines.append(f"Total load: {total_load} hours. Total capacity: {total_cap} hours. Over-allocated: {len(over)}. Ordering violations: {len(violations)}.")
    lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)
    sys.exit(1 if over or violations else 0)


if __name__ == "__main__":
    main()
