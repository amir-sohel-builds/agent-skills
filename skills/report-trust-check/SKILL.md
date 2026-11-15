---
name: report-trust-check
description: Audit the data behind a report. Use when a number looks wrong or nobody trusts it yet, and you need stale rows, missing values, and duplicates named and fixed in the open.
---

# Report trust check

## Inputs
- A CSV export of the data behind the report. Work from the same rows the report reads.

## Run
```bash
python3 scripts/check_csv.py --file export.csv --date-col updated_at --stale-days 7 --key-col id
```

## Output
A trust report: rows checked, missing values per column, duplicate keys, stale rows, and unreadable dates.

## Rules
- Treat every "this number looks wrong" as a bug report, not an argument.
- Fix the data first. A report on bad data is a prettier way to be wrong.
- Say what you could not check, and why.
- The check runs on the export, not on a screenshot of the dashboard.

## What it does not do
It does not fix the data. It names exactly what is wrong, in the open, so the fix is obvious.
