#!/usr/bin/env python3
"""Validate the harness: config, size limits, frontmatter, relative links, adapter sync and active plans.

Usage: lint.py    (exit 1 when any check fails)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

import sync
from common import (
    ABSTRACT_TOOLS,
    AGENTS_DIR,
    KNOWN_TARGETS,
    MODEL_HINTS,
    ROOT,
    HarnessError,
    load_config,
    rel,
    split_frontmatter,
)

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
CHECKBOX_RE = re.compile(r"^\s*[-*] \[[ xX]\] ", re.MULTILINE)
DOC_ROOTS = ("docs", ".agents", "ai", "examples")
TOP_LEVEL_DOCS = ("AGENTS.md", "CLAUDE.md", "README.md", "CONTRIBUTING.md")


class Lint:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks = 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def run(self, name: str, func: Any, *args: Any) -> None:
        self.checks += 1
        try:
            func(*args)
        except HarnessError as exc:
            self.error(f"{name}: {exc}")


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def canonical_markdown_files() -> list[Path]:
    files = [ROOT / name for name in TOP_LEVEL_DOCS if (ROOT / name).is_file()]
    for root in DOC_ROOTS:
        files += sorted((ROOT / root).rglob("*.md"))
    return files


# --------------------------------------------------------------------------- checks


def check_config(lint: Lint, config: dict[str, Any]) -> None:
    targets = config.get("targets")
    if not isinstance(targets, list) or not targets:
        lint.error("harness.config.yaml: 'targets' must be a non-empty list")
    else:
        for target in targets:
            if target not in KNOWN_TARGETS:
                lint.error(f"harness.config.yaml: unknown target '{target}' (known: {', '.join(KNOWN_TARGETS)})")
    for key in ("protected_paths", "secret_files", "deny_commands"):
        value = config.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            lint.error(f"harness.config.yaml: '{key}' must be a list of strings")
    for key in ("agents_md_max_lines", "skill_max_lines", "agent_max_lines"):
        if not isinstance((config.get("limits") or {}).get(key), int):
            lint.error(f"harness.config.yaml: 'limits.{key}' must be an integer")


def check_claude_md(lint: Lint) -> None:
    path = ROOT / "CLAUDE.md"
    if not path.is_file() or "@AGENTS.md" not in path.read_text(encoding="utf-8"):
        lint.error("CLAUDE.md must exist and import '@AGENTS.md'")


def check_sizes(lint: Lint, limits: dict[str, Any]) -> None:
    agents_md = ROOT / "AGENTS.md"
    if not agents_md.is_file():
        lint.error("AGENTS.md is missing")
        return
    max_lines = limits.get("agents_md_max_lines", 150)
    if line_count(agents_md) > max_lines:
        lint.error(f"AGENTS.md has {line_count(agents_md)} lines (limit {max_lines}); move details to docs/")
    for pattern, key in (("skills/*/SKILL.md", "skill_max_lines"), ("agents/*.md", "agent_max_lines")):
        limit = limits.get(key, 300)
        for path in sorted(AGENTS_DIR.glob(pattern)):
            if line_count(path) > limit:
                lint.error(f"{rel(path)} has {line_count(path)} lines (limit {limit}); split into supporting files")


def check_skills(lint: Lint) -> None:
    for skill_dir in sorted(p for p in (AGENTS_DIR / "skills").iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            lint.error(f"{rel(skill_dir)}: missing SKILL.md")
            continue
        meta, _ = split_frontmatter(skill_md.read_text(encoding="utf-8"), skill_md)
        name, description = meta.get("name"), meta.get("description")
        if name != skill_dir.name:
            lint.error(f"{rel(skill_md)}: 'name' must equal the directory name '{skill_dir.name}'")
        if not isinstance(name, str) or not sync.NAME_RE.match(name) or len(name) > 64:
            lint.error(f"{rel(skill_md)}: 'name' must be lowercase kebab-case, max 64 chars")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            lint.error(f"{rel(skill_md)}: 'description' is required (max 1024 chars) and should say when to use it")


def check_agents(lint: Lint) -> None:
    for path in sorted((AGENTS_DIR / "agents").glob("*.md")):
        meta, _ = split_frontmatter(path.read_text(encoding="utf-8"), path)
        if meta.get("name") != path.stem:
            lint.error(f"{rel(path)}: 'name' must equal the file name '{path.stem}'")
        if not isinstance(meta.get("description"), str) or not meta["description"].strip():
            lint.error(f"{rel(path)}: 'description' is required")
        tools = meta.get("tools")
        if not isinstance(tools, list) or not tools or any(t not in ABSTRACT_TOOLS for t in tools):
            lint.error(f"{rel(path)}: 'tools' must be a non-empty list from {list(ABSTRACT_TOOLS)}")
        if meta.get("model_hint") not in MODEL_HINTS:
            lint.error(f"{rel(path)}: 'model_hint' must be one of {list(MODEL_HINTS)}")


def check_commands(lint: Lint) -> None:
    for path in sorted((AGENTS_DIR / "commands").glob("*.md")):
        meta, _ = split_frontmatter(path.read_text(encoding="utf-8"), path)
        if not isinstance(meta.get("description"), str) or not meta["description"].strip():
            lint.error(f"{rel(path)}: 'description' is required")


def iter_links(text: str) -> list[tuple[int, str]]:
    links, in_fence = [], False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK_RE.finditer(INLINE_CODE_RE.sub("", line)):
            links.append((number, match.group(1)))
    return links


def check_links(lint: Lint) -> None:
    for path in canonical_markdown_files():
        for number, target in iter_links(path.read_text(encoding="utf-8")):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target_path = target.split("#", 1)[0].split("?", 1)[0]
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                lint.error(f"{rel(path)}:{number}: broken link '{target}'")


def check_sync(lint: Lint) -> None:
    outputs = sync.compute_outputs(sync.load_sources())
    if sync.check(outputs, sync.find_orphans(outputs)) != 0:
        lint.error("adapters out of sync (details above); run `make harness-sync`")


def check_active_plans(lint: Lint) -> None:
    for path in sorted((ROOT / "docs" / "plans" / "active").glob("*.md")):
        if not CHECKBOX_RE.search(path.read_text(encoding="utf-8")):
            lint.error(f"{rel(path)}: active plans need a checklist ('- [ ] step')")


def check_hooks_executable(lint: Lint) -> None:
    for path in sorted((ROOT / "scripts" / "hooks").glob("*.sh")):
        if not os.access(path, os.X_OK):
            lint.error(f"{rel(path)}: must be executable (chmod +x; git update-index --chmod=+x)")


def main() -> int:
    lint = Lint()
    try:
        config = load_config()
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    lint.run("config", check_config, lint, config)
    lint.run("claude", check_claude_md, lint)
    lint.run("sizes", check_sizes, lint, config.get("limits") or {})
    lint.run("skills", check_skills, lint)
    lint.run("agents", check_agents, lint)
    lint.run("commands", check_commands, lint)
    lint.run("links", check_links, lint)
    lint.run("sync", check_sync, lint)
    lint.run("plans", check_active_plans, lint)
    lint.run("hooks", check_hooks_executable, lint)

    if lint.errors:
        print(f"harness-lint: {len(lint.errors)} problem(s):", file=sys.stderr)
        for message in lint.errors:
            print(f"  - {message}", file=sys.stderr)
        return 1
    print(f"harness-lint: OK ({lint.checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
