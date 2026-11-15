#!/usr/bin/env python3
"""Score risks by likelihood times impact, sort, and flag the top ones."""
import argparse
import json


def main():
    p = argparse.ArgumentParser(description="Score and sort a risk register.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    if isinstance(data, list):
        data = {"risks": data}
    risks = []
    for r in data.get("risks", []):
        r = dict(r)
        r["score"] = r.get("likelihood", 0) * r.get("impact", 0)
        risks.append(r)
    open_risks = sorted([r for r in risks if r.get("status") == "open"],
                        key=lambda r: r["score"], reverse=True)
    closed_risks = [r for r in risks if r.get("status") != "open"]
    top = [r for r in open_risks if r["score"] >= 15]
    lines = ["# Risk register\n"]
    if top:
        lines.append("## Top risks (score 15 or more)\n")
        for r in top:
            lines.append(f"- **{r['id']}** {r['title']} (score {r['score']}, owner: {r.get('owner') or 'NONE'})")
        lines.append("")
    lines.append("## Open risks\n")
    lines.append("| ID | Risk | L | I | Score | Owner | Mitigation |")
    lines.append("| --- | --- | ---: | ---: | ---: | --- | --- |")
    for r in open_risks:
        lines.append(f"| {r['id']} | {r['title']} | {r.get('likelihood')} | {r.get('impact')} | {r['score']} | {r.get('owner') or 'NONE'} | {r.get('mitigation') or 'NONE'} |")
    lines.append("")
    flags = []
    for r in open_risks:
        if not r.get("owner"):
            flags.append(f"{r['id']} has no owner")
        if not r.get("mitigation"):
            flags.append(f"{r['id']} has no mitigation")
    if flags:
        lines.append("## Flags\n")
        for f in flags:
            lines.append(f"- {f}")
        lines.append("")
    if closed_risks:
        lines.append("## Closed\n")
        for r in closed_risks:
            lines.append(f"- {r['id']} {r['title']} (score {r['score']})")
        lines.append("")
    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
