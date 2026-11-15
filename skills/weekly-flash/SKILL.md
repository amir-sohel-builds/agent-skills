---
name: weekly-flash
description: Turn the week's shipped work into a one-page flash report. Use at the end of the week, when engineering, product, and design need to see what shipped, what broke, and what is next, without a meeting.
---

# Weekly flash

## Inputs
- `examples/week.json` shows the shape: a week label, and three lists, shipped, fixed, and next, each item one line with an optional link and an optional `by` name.

## Run
```bash
python3 scripts/flash.py --input week.json --output FLASH.md
```

## Output
A one-page report: Shipped, Fixed, Next, each a short list with links.

## Rules
- One line per item. If an item needs a paragraph, it is two items.
- Name the people behind the work, not only the work.
- Same time every week. Regular beats thorough.
- If nothing shipped, say so. A flash report that always says "great week" is ignored by week three.

## What it does not do
It does not collect the items. The TPM collects them during the week, the tool renders the page.
