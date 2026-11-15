#!/usr/bin/env python3
"""Build a dependency map from work items. Finds cycles, orphans, critical path."""
import argparse
import json
import sys


def main():
    p = argparse.ArgumentParser(description="Build a dependency map from work items.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    if isinstance(data, list):
        data = {"workstreams": data}
    items = {w["id"]: w for w in data.get("workstreams", [])}
    warnings = []
    for w in data.get("workstreams", []):
        for dep in w.get("depends_on", []):
            if dep not in items:
                warnings.append(f"unknown dependency: {w['id']} depends on missing id '{dep}'")
    # Cycle detection, depth-first, recording the cycle path.
    state = {}
    cycles = []

    def visit(node, path):
        state[node] = "gray"
        path = path + [node]
        for dep in items[node].get("depends_on", []):
            if dep not in items:
                continue
            if state.get(dep) == "gray":
                cycles.append(path[path.index(dep):] + [dep])
            elif state.get(dep) != "black":
                visit(dep, path)
        state[node] = "black"

    for node in items:
        if state.get(node) != "black":
            visit(node, [])
    # Levels: longest path from a root. Critical path: the longest chain.
    memo = {}

    def longest(node, seen):
        if node in memo:
            return memo[node]
        if node in seen:
            return (0, [node])
        best = (1, [node])
        for dep in items[node].get("depends_on", []):
            if dep not in items:
                continue
            length, path = longest(dep, seen | {node})
            if length + 1 > best[0]:
                best = (length + 1, path + [node])
        memo[node] = best
        return best

    levels = {}
    for node in items:
        length, _ = longest(node, set())
        levels.setdefault(length - 1, []).append(node)
    critical = max((longest(n, set()) for n in items), key=lambda t: t[0], default=(0, []))
    depended_on = {d for w in items.values() for d in w.get("depends_on", []) if d in items}
    orphans = [n for n, w in items.items() if not w.get("depends_on") and n not in depended_on]
    for n in orphans:
        warnings.append(f"orphan: {n} ({items[n]['name']}) has no dependencies and nothing depends on it")
    lines = ["# Dependency map\n"]
    for level in sorted(levels):
        lines.append(f"## Level {level}\n")
        for n in sorted(levels[level]):
            w = items[n]
            deps = ", ".join(w.get("depends_on", [])) or "none"
            lines.append(f"- **{n}** {w['name']} ({w.get('owner', 'no owner')}), depends on: {deps}")
        lines.append("")
    lines.append("## Critical path\n")
    lines.append(" -> ".join(critical[1]) + f" ({critical[0]} items)\n")
    if warnings:
        lines.append("## Warnings\n")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")
    if cycles:
        lines.append("## Cycles (must fix)\n")
        for c in cycles:
            lines.append("- " + " -> ".join(c))
        lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)
    sys.exit(1 if cycles else 0)


if __name__ == "__main__":
    main()
