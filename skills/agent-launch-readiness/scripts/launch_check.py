#!/usr/bin/env python3
"""Check an agent spec before it goes live. GO only when every blocking check passes."""
import argparse
import json
import sys


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def text(value):
    return value.strip() if isinstance(value, str) else ""


def fmt(n):
    return f"{n:g}"


def evaluate(spec):
    ev = spec.get("eval") or {}
    rb = spec.get("rollback") or {}
    sources = spec.get("sources") or []
    actions = spec.get("actions") or []
    threshold = num(ev.get("threshold"))
    if threshold is None:
        threshold = 90.0
    rate = num(ev.get("pass_rate"))
    cap = num(spec.get("cost_cap_monthly"))
    unapproved = [text(a.get("name")) or "unnamed action" for a in actions
                  if a.get("writes") is True and a.get("human_approval") is not True]
    if rate is None:
        rate_reason = "no pass rate given"
    else:
        rate_reason = f"pass rate {fmt(rate)}% is below the {fmt(threshold)}% threshold"
    checks = [
        ("A1", "Named owner", bool(text(spec.get("owner"))), "no owner named"),
        ("A2", "Approved sources listed",
         isinstance(sources, list) and any(text(s) for s in sources), "no sources listed"),
        ("A3", "Refuses when it cannot verify", spec.get("refuses_without_source") is True,
         "refuses_without_source is not true"),
        ("A4", "Eval suite exists", ev.get("suite") is True, "no eval suite"),
        ("A5", "Eval pass rate meets the threshold", rate is not None and rate >= threshold, rate_reason),
        ("A6", "Rollback in one step", rb.get("one_step") is True, "rollback is not one step"),
        ("A7", "Prompts are versioned", rb.get("prompt_versioned") is True, "prompts are not versioned"),
        ("A8", "Monthly cost cap set", cap is not None and cap > 0, "no cost cap"),
        ("A9", "Write actions need human approval", not unapproved,
         "no human approval on: " + ", ".join(unapproved)),
        ("A10", "Runs with the caller's permissions", spec.get("runs_as_caller") is True,
         "runs on a shared credential"),
        ("A11", "Logs and traces are on", spec.get("observability") is True, "no logs or traces"),
        ("A12", "Privacy reviewed when personal data is handled",
         spec.get("handles_pii") is not True or spec.get("pii_review_done") is True,
         "handles personal data, privacy review not done"),
    ]
    blocking = [(i, q, r) for i, q, ok, r in checks if not ok]
    warnings = []
    if not text(spec.get("escalation_contact")):
        warnings.append("No escalation contact named.")
    if rate is not None and rate >= threshold and rate - threshold < 3:
        warnings.append(f"Pass rate {fmt(rate)}% is within 3 points of the {fmt(threshold)}% threshold.")
    return blocking, warnings, len(checks) - len(blocking), len(checks)


def render(spec):
    blocking, warnings, passed, total = evaluate(spec)
    verdict = "GO" if not blocking else "NO-GO"
    name = text(spec.get("name")) or "unnamed agent"
    lines = [f"# Agent launch readiness: {name}", "", f"Verdict: {verdict}", ""]
    if blocking:
        lines += ["## Blocking", ""]
        lines += [f"- **{i}** {q} ({r})" for i, q, r in blocking]
        lines.append("")
    if warnings:
        lines += ["## Warnings", ""]
        lines += [f"- {w}" for w in warnings]
        lines.append("")
    lines.append(f"Passed: {passed}/{total}")
    return "\n".join(lines), verdict


def main():
    p = argparse.ArgumentParser(description="Check an agent spec before it goes live.")
    p.add_argument("--input", required=True)
    args = p.parse_args()
    with open(args.input) as f:
        spec = json.load(f)
    if not isinstance(spec, dict):
        print("The spec must be a JSON object.", file=sys.stderr)
        sys.exit(2)
    out, verdict = render(spec)
    print(out)
    sys.exit(0 if verdict == "GO" else 1)


if __name__ == "__main__":
    main()
