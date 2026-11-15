#!/usr/bin/env python3
"""Evaluate a launch checklist. GO only when every required item is yes."""
import argparse
import json
import sys


def main():
    p = argparse.ArgumentParser(description="Evaluate a launch checklist.")
    p.add_argument("--input", required=True)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    if isinstance(data, list):
        data = {"items": data}
    items = data.get("items", [])
    reasons = []
    na = []
    for item in items:
        status = (item.get("status") or "").strip().lower()
        if status == "na":
            na.append(item)
        elif status == "yes":
            continue
        else:
            reason = "not answered" if not status else f"status is {status}"
            reasons.append((item, reason))
    verdict = "GO" if not reasons else "NO-GO"
    print("# Launch readiness\n")
    print(f"Verdict: {verdict}\n")
    if reasons:
        print("## Why not\n")
        for item, reason in reasons:
            print(f"- **{item['id']}** {item['question']} ({reason}, owner: {item.get('owner') or 'NONE'})")
            print(f"  - Evidence: {item.get('evidence') or 'none given'}")
        print("")
    if na:
        print("## Not applicable\n")
        for item in na:
            print(f"- {item['id']} {item['question']}")
        print("")
    passed = len([i for i in items if (i.get("status") or "").strip().lower() == "yes"])
    print(f"Passed: {passed}/{len(items)}")
    sys.exit(0 if verdict == "GO" else 1)


if __name__ == "__main__":
    main()
