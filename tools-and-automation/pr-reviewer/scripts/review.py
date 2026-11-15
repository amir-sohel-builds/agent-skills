#!/usr/bin/env python3
"""PR Reviewer: scan a pull request diff or a set of files for secrets,
dangerous patterns, and code quality issues. Posts a review with a verdict.

Modes:
  --diff FILE    Scan a unified diff (added lines only).
  --files PATH   Scan files or directories (all lines). Repeatable.
  --exclude PATH Skip a file or directory. Repeatable.
  --output FILE  Write the review markdown (default: stdout only).

Exit 0: APPROVE or COMMENT. Exit 1: REQUEST CHANGES (critical or high findings).

This is a first pass, not a full static analysis tool. It catches the
common, high-signal issues: secrets in code, code that runs arbitrary input,
and changes that weaken the review process itself. It never executes the code
it reviews.
"""
import argparse
import os
import re
import sys

FOOTER = "Reviewed by PR Reviewer bot, created by Amir Sohel (TPM)"

SECRET_PATTERNS = [
    ("Critical", "AWS access key", re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key in code. Rotate it and move it to a secret store."),
    ("Critical", "Private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "Private key in code. Remove it and rotate the key."),
    ("Critical", "GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token in code. Revoke it and move it to a secret store."),
    ("Critical", "JWT", re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"), "JWT in code. Tokens do not belong in source."),
    ("Critical", "Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token in code. Revoke it."),
    ("High", "Password assignment", re.compile(r"(?i)(password|passwd|pwd)\s*=\s*[\"'][^\"']{4,}[\"']"), "Password assigned in code. Use a secret store."),
    ("High", "API key assignment", re.compile(r"(?i)api[_-]?key\s*=\s*[\"'][^\"']{4,}[\"']"), "API key assigned in code. Use a secret store."),
    ("High", "Bearer token", re.compile(r"Authorization:\s*Bearer\s+\S+"), "Bearer token in code. Use a secret store."),
]

CODE_PATTERNS = [
    ("High", "eval or exec", re.compile(r"\b(eval|exec)\s*\("), "eval and exec run arbitrary code. Do not run untrusted input through them."),
    ("High", "Shell command", re.compile(r"os\.system\s*\(|subprocess\.(run|Popen|call)\s*\([^)]*shell\s*=\s*True"), "Runs a shell command. Use list arguments and no shell."),
    ("High", "Pickle load", re.compile(r"pickle\.(loads?|load)\s*\("), "Pickle can run arbitrary code on load. Do not unpickle untrusted data."),
    ("High", "Unsafe YAML load", re.compile(r"yaml\.load\s*\((?![^)]*SafeLoader)"), "yaml.load without SafeLoader can run arbitrary code. Use yaml.safe_load."),
    ("High", "Pipe to shell", re.compile(r"(curl|wget)\b[^|]*\|\s*(bash|sh)\b"), "Piping a download straight to a shell runs untrusted code."),
    ("High", "TLS verification off", re.compile(r"verify\s*=\s*False"), "TLS verification is off. Requests can be intercepted."),
    ("Medium", "Weak hash", re.compile(r"hashlib\.(md5|sha1)\s*\("), "MD5 and SHA1 are broken. Use SHA256 or better."),
    ("Medium", "Weak random for secrets", re.compile(r"random\.(random|randint|choice)\s*\("), "random is not safe for secrets. Use the secrets module."),
    ("Medium", "SQL string building", re.compile(r"\.execute\s*\([^)]*(\+|f\")"), "SQL built from strings invites injection. Use parameters."),
    ("Medium", "SQL percent formatting", re.compile(r"\.execute\s*\([^)]*%\s*\("), "SQL built with percent formatting invites injection. Use parameters."),
    ("Medium", "innerHTML", re.compile(r"\b(innerHTML|dangerouslySetInnerHTML)\b"), "innerHTML can inject scripts. Use text content or a sanitizer."),
    ("Medium", "chmod 777", re.compile(r"chmod\s+777"), "chmod 777 gives everyone full access. Use the least privilege that works."),
]

QUALITY_PATTERNS = [
    ("Low", "TODO or FIXME", re.compile(r"\b(TODO|FIXME|HACK)\b"), "Left a marker in the change. Say when it gets done, or do it now."),
    ("Low", "console.log left in", re.compile(r"console\.log\s*\("), "console.log left in the change."),
    ("Low", "debugger left in", re.compile(r"\bdebugger\s*;"), "debugger statement left in the change."),
]

CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".rb", ".go", ".java", ".php", ".c", ".cpp"}
KEY_EXTS = {".pem", ".key", ".p12", ".pfx"}


def check_line(line, patterns):
    return [(sev, name, msg) for sev, name, pattern, msg in patterns if pattern.search(line)]


def parse_diff(text):
    """Yield (path, line_number, line) for added lines, plus file-level notes."""
    path = None
    new_no = 0
    files = set()
    for line in text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split(" ")
            if len(parts) >= 4 and parts[3].startswith("b/"):
                path = parts[3][2:]
                files.add(path)
            continue
        if line.startswith("+++ "):
            p = line[4:].strip()
            if p.startswith("b/"):
                p = p[2:]
            path = None if p == "/dev/null" else p
            if path:
                files.add(path)
            continue
        if line.startswith("@@ "):
            m = re.search(r"\+(\d+)", line)
            new_no = int(m.group(1)) if m else 0
            continue
        if line.startswith("Binary files "):
            if path:
                yield ("__binary__", path, 0, line)
            continue
        if path is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            yield (path, new_no, line[1:])
            new_no += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        else:
            new_no += 1


def scan_diff(text):
    findings = []
    files = set()
    added = 0
    for entry in parse_diff(text):
        if entry[0] == "__binary__":
            findings.append((entry[1], 0, entry[3], "Low", "Binary file", "Binary file added. Review it by hand."))
            files.add(entry[1])
            continue
        path, line_no, line = entry
        files.add(path)
        added += 1
        for sev, name, msg in check_line(line, SECRET_PATTERNS):
            findings.append((path, line_no, line, sev, name, msg))
        ext = os.path.splitext(path)[1].lower()
        if ext in CODE_EXTS:
            for sev, name, msg in check_line(line, CODE_PATTERNS):
                findings.append((path, line_no, line, sev, name, msg))
            for sev, name, msg in check_line(line, QUALITY_PATTERNS):
                findings.append((path, line_no, line, sev, name, msg))
    for path in files:
        ext = os.path.splitext(path)[1].lower()
        if ext in KEY_EXTS:
            findings.append((path, 0, "", "Critical", "Private key file", "Private key file added. Remove it and rotate the key."))
        if path.startswith(".github/workflows/") or path == ".github/scripts/review.py":
            findings.append((path, 0, "", "High", "Reviewer changed", "This change touches the review process itself. Review it by hand."))
    return findings, added, len(files)


def scan_files(paths, excludes):
    findings = []
    checked = 0
    self_path = os.path.abspath(__file__)
    for base in paths:
        if os.path.isfile(base):
            all_files = [base]
        else:
            all_files = []
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
                for fn in filenames:
                    all_files.append(os.path.join(dirpath, fn))
        for f in all_files:
            if any(f == e or f.startswith(e.rstrip("/") + "/") for e in excludes):
                continue
            if os.path.abspath(f) == self_path:
                continue
            if os.path.splitext(f)[1].lower() in (".pyc", ".zip", ".png", ".jpg", ".jpeg", ".pdf"):
                continue
            try:
                with open(f, errors="ignore") as fh:
                    lines = fh.read().splitlines()
            except OSError:
                continue
            checked += 1
            ext = os.path.splitext(f)[1].lower()
            for i, line in enumerate(lines, 1):
                for sev, name, msg in check_line(line, SECRET_PATTERNS):
                    findings.append((f, i, line, sev, name, msg))
                if ext in CODE_EXTS:
                    for sev, name, msg in check_line(line, CODE_PATTERNS):
                        findings.append((f, i, line, sev, name, msg))
                    for sev, name, msg in check_line(line, QUALITY_PATTERNS):
                        findings.append((f, i, line, sev, name, msg))
    return findings, checked, 0


def verdict(findings):
    sevs = {f[3] for f in findings}
    if "Critical" in sevs or "High" in sevs:
        return "REQUEST CHANGES"
    if "Medium" in sevs:
        return "COMMENT"
    return "APPROVE"


def render(findings, scope):
    counts = {s: sum(1 for f in findings if f[3] == s) for s in ("Critical", "High", "Medium", "Low")}
    v = verdict(findings)
    lines = ["# PR Review\n", f"## Verdict: {v}\n"]
    lines.append(f"{scope}. Found {len(findings)} findings: "
                 f"{counts['Critical']} critical, {counts['High']} high, "
                 f"{counts['Medium']} medium, {counts['Low']} low.\n")
    if not findings:
        lines.append("No findings. Clean change.\n")
    for sev in ("Critical", "High", "Medium", "Low"):
        group = [f for f in findings if f[3] == sev]
        if not group:
            continue
        lines.append(f"## {sev}\n")
        for path, line_no, line, _, name, msg in group:
            where = f"{path}:{line_no}" if line_no else path
            lines.append(f"- **{where}** {name}: {msg}")
            if line.strip():
                lines.append(f"  `{line.strip()}`")
        lines.append("")
    lines.append("---\n")
    lines.append(FOOTER)
    lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Review a PR diff or files for security and quality.")
    p.add_argument("--diff", default=None)
    p.add_argument("--files", nargs="*", default=[])
    p.add_argument("--exclude", action="append", default=[])
    p.add_argument("--output", default=None)
    args = p.parse_args()
    if args.diff:
        with open(args.diff) as f:
            findings, added, nfiles = scan_diff(f.read())
        scope = f"Checked {added} added lines across {nfiles} files"
    elif args.files:
        findings, checked, _ = scan_files(args.files, args.exclude)
        scope = f"Checked {checked} files"
    else:
        p.error("give --diff or --files")
    text = render(findings, scope)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    print(text)
    sys.exit(1 if verdict(findings) == "REQUEST CHANGES" else 0)


if __name__ == "__main__":
    main()
