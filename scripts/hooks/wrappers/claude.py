#!/usr/bin/env python3
"""Thin Claude Code hook adapter: turns the JSON payload on stdin into arguments for scripts/hooks/<hook>.sh.

Usage (from .claude/settings.json): claude.py <hook-name>
Exit codes are passed through, so exit 2 from a hook blocks the tool call / keeps the agent working.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]
PATH_KEYS = ("file_path", "notebook_path")
PATHLESS_HOOKS = {"check-on-stop"}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: claude.py <hook-name>", file=sys.stderr)
        return 1
    hook = sys.argv[1]
    script = HOOKS_DIR / f"{hook}.sh"
    if not script.is_file():
        print(f"claude.py: unknown hook '{hook}'", file=sys.stderr)
        return 1

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"claude.py: invalid hook payload: {exc}", file=sys.stderr)
        return 1

    # Avoid infinite loops: a Stop hook that already blocked once lets the agent stop.
    if payload.get("stop_hook_active"):
        return 0

    tool_input = payload.get("tool_input") or {}
    paths = [tool_input[k] for k in PATH_KEYS if isinstance(tool_input.get(k), str)]
    if hook not in PATHLESS_HOOKS and not paths:
        return 0

    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or None
    return subprocess.run(["bash", str(script), *paths], cwd=cwd, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
