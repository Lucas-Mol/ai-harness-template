#!/usr/bin/env python3
"""Report harness entropy: stale plans, unreferenced docs, old TODOs, context files near their size limit.

Only reports — never deletes or edits anything.

Usage: gc.py [--output report.md]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

from common import AGENTS_DIR, ROOT, HarnessError, load_config, rel
from lint import canonical_markdown_files, iter_links, line_count

LAST_UPDATED_RE = re.compile(r"Last updated:\*{0,2}\s*(\d{4}-\d{2}-\d{2})")
TODO_RE = r"\b(TODO|FIXME|HACK)(\(|:)"
UNREFERENCED_EXEMPT = {"README.md", "TEMPLATE.md", "0000-template.md"}
NEAR_LIMIT_RATIO = 0.8
DAY = 86_400


def git(*args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None
    return result.stdout if result.returncode == 0 else None


def last_touched(path: Path) -> float:
    """Most recent of: 'Last updated:' field, last git commit, file mtime."""
    candidates = [path.stat().st_mtime]
    match = LAST_UPDATED_RE.search(path.read_text(encoding="utf-8"))
    if match:
        try:
            candidates.append(datetime.strptime(match.group(1), "%Y-%m-%d").timestamp())
        except ValueError:
            pass
    committed = git("log", "-1", "--format=%ct", "--", rel(path))
    if committed and committed.strip():
        candidates.append(float(committed.strip()))
    return max(candidates)


def stale_plans(stale_after_days: int) -> list[str]:
    now, rows = time.time(), []
    for path in sorted((ROOT / "docs" / "plans" / "active").glob("*.md")):
        age_days = int((now - last_touched(path)) // DAY)
        if age_days > stale_after_days:
            rows.append(f"| `{rel(path)}` | {age_days} days |")
    return rows


def unreferenced_docs() -> list[str]:
    referenced: set[Path] = set()
    for source in canonical_markdown_files():
        for _, target in iter_links(source.read_text(encoding="utf-8")):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            resolved = (source.parent / target.split("#", 1)[0]).resolve()
            if resolved != source.resolve():
                referenced.add(resolved / "README.md" if resolved.is_dir() else resolved)
    completed = (ROOT / "docs" / "plans" / "completed").resolve()
    rows = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        resolved = path.resolve()
        if path.name in UNREFERENCED_EXEMPT or completed in resolved.parents or resolved in referenced:
            continue
        rows.append(f"| `{rel(path)}` |")
    return rows


def old_todos(max_age_days: int) -> list[str]:
    listing = git("grep", "-n", "-I", "-E", TODO_RE)
    if listing is None:
        return []
    now, rows = time.time(), []
    for line in listing.splitlines():
        file_name, line_no, text = line.split(":", 2)
        blame = git("blame", "-L", f"{line_no},{line_no}", "--porcelain", "--", file_name) or ""
        match = re.search(r"^author-time (\d+)$", blame, re.MULTILINE)
        if not match:
            continue
        age_days = int((now - int(match.group(1))) // DAY)
        if age_days > max_age_days:
            snippet = text.strip().replace("|", "\\|")[:100]
            rows.append(f"| `{file_name}:{line_no}` | {age_days} days | {snippet} |")
    return rows


def near_limit(limits: dict) -> list[str]:
    checks = [(ROOT / "AGENTS.md", limits.get("agents_md_max_lines", 150))]
    checks += [(p, limits.get("skill_max_lines", 300)) for p in sorted(AGENTS_DIR.glob("skills/*/SKILL.md"))]
    checks += [(p, limits.get("agent_max_lines", 200)) for p in sorted(AGENTS_DIR.glob("agents/*.md"))]
    rows = []
    for path, limit in checks:
        if path.is_file() and line_count(path) >= limit * NEAR_LIMIT_RATIO:
            rows.append(f"| `{rel(path)}` | {line_count(path)} / {limit} |")
    return rows


def section(title: str, header: str, rows: list[str], empty: str) -> str:
    if not rows:
        return f"## {title}\n\n{empty}\n"
    separator = "|" + "|".join("---" for _ in header.strip("|").split("|")) + "|"
    return f"## {title}\n\n{header}\n{separator}\n" + "\n".join(rows) + "\n"


def build_report(config: dict) -> tuple[str, int]:
    plans_cfg, gc_cfg = config.get("plans") or {}, config.get("gc") or {}
    stale_days = int(plans_cfg.get("stale_after_days", 14))
    todo_days = int(gc_cfg.get("todo_max_age_days", 90))
    sections = [
        ("Stale active plans", "| Plan | Last touched |", stale_plans(stale_days),
         f"No active plan older than {stale_days} days."),
        ("Unreferenced docs", "| Doc |", unreferenced_docs(), "Every doc is linked from somewhere."),
        ("Old TODO / FIXME / HACK", "| Location | Age | Text |", old_todos(todo_days),
         f"No TODO older than {todo_days} days (requires git)."),
        ("Context files near their size limit", "| File | Lines / limit |", near_limit(config.get("limits") or {}),
         "All context files are below 80% of their limit."),
    ]
    findings = sum(len(rows) for _, _, rows, _ in sections)
    body = "\n".join(section(*s) for s in sections)
    report = (
        f"# Harness GC report — {date.today().isoformat()}\n\n"
        f"{findings} finding(s). This report never deletes anything: "
        "archive, link, fix or delete items deliberately.\n\n" + body
    )
    return report, findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, help="write the report to this file instead of stdout")
    args = parser.parse_args()
    try:
        report, findings = build_report(load_config())
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"harness-gc: {findings} finding(s) written to {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
