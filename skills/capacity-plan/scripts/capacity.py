#!/usr/bin/env python3
"""Match committed work against team capacity, by person and by week."""
import argparse
import json
import sys
from collections import defaultdict


def main():
    p = argparse.ArgumentParser(description="Check committed work against capacity.")
    p.add_argument("--input", required=True)
    args = p.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    available = {p["name"]: p["hours_per_week"] for p in data.get("people", [])}
    committed = defaultdict(lambda: defaultdict(int))
    for w in data.get("work", []):
        committed[w["week"]][w["owner"]] += w["hours"]
    over = 0
    print("# Capacity plan\n")
    for week in sorted(committed):
        print(f"## Week {week}\n")
        print("| Person | Available | Committed | Status |")
        print("| --- | ---: | ---: | --- |")
        for person in sorted(available):
            have = available[person]
            done = committed[week].get(person, 0)
            if done > have:
                status = "OVER"
                over += 1
            elif done < have / 2:
                status = "UNDER"
            else:
                status = "OK"
            print(f"| {person} | {have} | {done} | {status} |")
        print()
    print(f"Over-allocated: {over}")
    sys.exit(1 if over else 0)


if __name__ == "__main__":
    main()
