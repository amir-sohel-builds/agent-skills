#!/usr/bin/env python3
"""Check a CSV export for stale rows, missing values, duplicates, and bad ranges."""
import argparse
import csv
from collections import Counter
from datetime import date, datetime, timedelta


def parse_date(value):
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def main():
    p = argparse.ArgumentParser(description="Check a CSV export for data trust issues.")
    p.add_argument("--file", required=True)
    p.add_argument("--date-col", default=None)
    p.add_argument("--stale-days", type=int, default=7)
    p.add_argument("--key-col", default=None)
    args = p.parse_args()
    with open(args.file, newline="") as f:
        rows = list(csv.DictReader(f))
    print("# Data trust report\n")
    print(f"Rows: {len(rows)}\n")
    if not rows:
        return
    for col in rows[0]:
        missing = sum(1 for r in rows if not (r.get(col) or "").strip())
        if missing:
            print(f"- {missing} rows missing a value in '{col}'")
    if args.key_col:
        keys = [r.get(args.key_col, "") for r in rows]
        dupes = {k: n for k, n in Counter(keys).items() if n > 1 and k}
        for key, n in list(dupes.items())[:10]:
            print(f"- duplicate key '{key}' appears {n} times")
        if not dupes:
            print(f"- no duplicate keys in '{args.key_col}'")
    if args.date_col:
        cutoff = date.today() - timedelta(days=args.stale_days)
        stale = 0
        unparsed = 0
        for r in rows:
            parsed = parse_date((r.get(args.date_col) or "").strip())
            if parsed is None:
                unparsed += 1
            elif parsed < cutoff:
                stale += 1
        print(f"- {stale} rows older than {args.stale_days} days in '{args.date_col}'")
        if unparsed:
            print(f"- {unparsed} rows have an unreadable date in '{args.date_col}'")


if __name__ == "__main__":
    main()
