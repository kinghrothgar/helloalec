#!/usr/bin/env python3
"""check_agents_md.py — Deterministic lint for an AGENTS.md / CLAUDE.md.

Stdlib-only. Exits non-zero on any error-level finding.

Checks:
  1. Line count under cap (default 150; --max-lines)
  2. Markdown link targets resolve on disk (error); backtick paths
     containing a slash resolve against the file's dir or git root (warning)
  3. Section-banner comments (# ---- foo ----, <!-- ==== -->)
  4. Hedging words (please, try to, should ideally, consider, maybe, ...)
  5. Duplicate bullets (normalised text appears more than once)
  6. @file references with no read/load instruction on the same line
  7. Bullets longer than 3 physical lines (warning)
  8. Prose paragraphs longer than 4 lines — narrative, not rules (warning)
  9. History phrases: "used to", "originally", "migrated from", ... (warning)
 10. Three or more mutating / human-only commands (op, kubectl apply, tk apply,
     helm install, ssh user@host, ...) — a runbook agents cannot run (warning)

Usage:
    python3 check_agents_md.py path/to/AGENTS.md
    python3 check_agents_md.py path/to/AGENTS.md --output json
    python3 check_agents_md.py path/to/AGENTS.md --max-lines 80
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List

DEFAULT_MAX_LINES = 150
MAX_BULLET_LINES = 3

HEDGES = [
    r"\bplease\b",
    r"\btry to\b",
    r"\bshould ideally\b",
    r"\bideally\b",
    r"\bconsider\b",
    r"\bmaybe\b",
    r"\bif possible\b",
    r"\bwhen you can\b",
    r"\bit would be (nice|good|great)\b",
    r"\bfeel free\b",
]
HEDGE_RE = re.compile("|".join(HEDGES), re.IGNORECASE)

BANNER_RE = re.compile(r"^\s*(#+\s*)?(-{4,}|={4,}|\*{4,})\s*\S.*(-{4,}|={4,}|\*{4,})\s*$|^\s*<!--\s*(-{4,}|={4,}).*-->\s*$")

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
TICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+/[A-Za-z0-9_./-]*|[A-Za-z0-9_.-]+\.(?:md|yaml|yml|json|sh|py|toml|txt))`")
AT_FILE_RE = re.compile(r"(?<![\w@])@([A-Za-z0-9_./-]+\.[A-Za-z]+)")
READ_VERB_RE = re.compile(r"\b(load|read|open|see|follow|consult)\b", re.IGNORECASE)

HISTORY_RE = re.compile(
    r"\b(we used to|used to be|originally|previously|historically|was replaced by|migrated from|"
    r"in the past|at the time|back when|no longer (?:used|needed))\b",
    re.IGNORECASE,
)
MAX_PROSE_LINES = 4

RUNBOOK_RE = re.compile(
    r"(^|[\s`$])(op (?:item|read|vault|signin)|kubectl (?:apply|delete|patch|exec|edit|scale|rollout)|"
    r"tk (?:apply|prune)|helm (?:install|upgrade|uninstall)|terraform (?:apply|destroy)|"
    r"talosctl (?:apply-config|bootstrap|reset|upgrade)|ansible-playbook|ssh \S+@)"
)

BULLET_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+")
CODE_FENCE_RE = re.compile(r"^\s*```")
URL_RE = re.compile(r"^[a-z]+://")


def norm(text: str) -> str:
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower().rstrip(".")


def looks_like_path(s: str) -> bool:
    if URL_RE.match(s) or s.startswith("#") or "..." in s:
        return False
    if any(ch in s for ch in "{}*<>$"):
        return False
    return "/" in s


def git_root(start: str) -> str:
    d = start
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return ""
        d = parent


def resolves(t: str, roots: List[str]) -> bool:
    return any(os.path.exists(os.path.normpath(os.path.join(r, t))) for r in roots if r)


def check(path: str, max_lines: int) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    base = os.path.dirname(os.path.abspath(path))
    roots = [base, git_root(base)]

    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    def add(level: str, rule: str, lineno: int, msg: str) -> None:
        findings.append({"level": level, "rule": rule, "line": lineno, "message": msg})

    if len(lines) > max_lines:
        add("error", "max-lines", 0, f"{len(lines)} lines; cap is {max_lines}")

    in_fence = False
    seen_bullets: Dict[str, int] = {}
    bullet_start = -1
    bullet_len = 0
    prose_start = -1
    prose_len = 0

    def close_bullet() -> None:
        nonlocal bullet_start, bullet_len
        if bullet_start >= 0 and bullet_len > MAX_BULLET_LINES:
            add("warning", "long-bullet", bullet_start + 1, f"bullet spans {bullet_len} lines (max {MAX_BULLET_LINES})")
        bullet_start, bullet_len = -1, 0

    def close_prose() -> None:
        nonlocal prose_start, prose_len
        if prose_start >= 0 and prose_len > MAX_PROSE_LINES:
            add("warning", "narrative", prose_start + 1, f"prose paragraph spans {prose_len} lines; rule or README?")
        prose_start, prose_len = -1, 0

    runbook_hits: List[int] = []

    for i, line in enumerate(lines):
        n = i + 1
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            close_bullet()
            close_prose()
            continue
        if RUNBOOK_RE.search(line):
            runbook_hits.append(n)
        if in_fence:
            continue

        if HISTORY_RE.search(line) and not line.lstrip().startswith("#"):
            add("warning", "history", n, f"history phrase: {HISTORY_RE.search(line).group(0)!r}")

        is_struct = BULLET_RE.match(line) or line.lstrip().startswith(("#", "|", ">"))
        if line.strip() == "" or is_struct:
            close_prose()
        elif bullet_start < 0:
            if prose_start < 0:
                prose_start = i
            prose_len += 1

        if BANNER_RE.match(line):
            add("error", "banner", n, "section-banner comment; use a heading")

        if HEDGE_RE.search(line) and not line.lstrip().startswith("#"):
            add("error", "hedge", n, f"hedging language: {HEDGE_RE.search(line).group(0)!r}")

        for m in AT_FILE_RE.finditer(line):
            if not READ_VERB_RE.search(line):
                add("error", "at-ref", n, f"@{m.group(1)} is not auto-loaded; add a read/load instruction")

        for t in set(MD_LINK_RE.findall(line)):
            if not URL_RE.match(t) and not resolves(t, roots):
                add("error", "dead-link", n, f"link target does not exist: {t}")
        for t in set(TICK_PATH_RE.findall(line)):
            if looks_like_path(t) and not resolves(t, roots):
                add("warning", "dead-path", n, f"path does not exist: {t}")

        if BULLET_RE.match(line):
            close_bullet()
            bullet_start, bullet_len = i, 1
            key = norm(BULLET_RE.sub("", line))
            if len(key) > 20:
                if key in seen_bullets:
                    add("error", "duplicate", n, f"duplicate of line {seen_bullets[key]}")
                else:
                    seen_bullets[key] = n
        elif bullet_start >= 0:
            if line.strip() == "" or line.lstrip().startswith("#"):
                close_bullet()
            else:
                bullet_len += 1
    close_bullet()
    close_prose()

    if len(runbook_hits) >= 3:
        add("warning", "runbook", runbook_hits[0],
            f"{len(runbook_hits)} mutating/human-only commands (op, kubectl apply, tk apply, ssh …); runbook for humans?")

    errors = sum(1 for f in findings if f["level"] == "error")
    return {"file": path, "lines": len(lines), "findings": findings, "errors": errors, "ok": errors == 0}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    ap.add_argument("--output", choices=["text", "json"], default="text")
    args = ap.parse_args()

    if not os.path.isfile(args.path):
        print(f"not a file: {args.path}", file=sys.stderr)
        return 2

    result = check(args.path, args.max_lines)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['file']}: {result['lines']} lines, {result['errors']} error(s)")
        for f in result["findings"]:
            loc = f"L{f['line']}" if f["line"] else "file"
            print(f"  {f['level']:7} {f['rule']:12} {loc:6} {f['message']}")
        print("OK" if result["ok"] else "FAIL")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
