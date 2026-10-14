#!/usr/bin/env python3
"""Bootstrap a new project from this template.

Asks for name, description, owner, stack and targets (or takes them as flags), replaces placeholders,
installs the chosen stack.mk and regenerates adapters. Removing examples/ and ai/ always asks first.

Usage: init.py [--name N] [--description D] [--owner @user] [--stack java|python|node|go|none]
               [--targets claude,copilot] [--remove-examples] [--remove-ai] [--yes]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from common import CONFIG_PATH, KNOWN_TARGETS, ROOT, HarnessError, rel

STACKS = ("java", "python", "node", "go", "none")
PLACEHOLDER_FILES = (
    "AGENTS.md", "harness.config.yaml", "LICENSE", ".github/CODEOWNERS", "docs/architecture/overview.md",
)
TEMPLATE_HISTORY = (
    "docs/plans/completed/0001-bootstrap-harness.md",
    "docs/plans/completed/0001-bootstrap-harness.spec.pt-BR.md",
)


def ask(question: str, default: str, value: str | None) -> str:
    if value is not None:
        return value
    if not sys.stdin.isatty():
        return default
    answer = input(f"{question} [{default}]: ").strip()
    return answer or default


def confirm(question: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        return False
    return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def replace_placeholders(values: dict[str, str]) -> None:
    for name in PLACEHOLDER_FILES:
        path = ROOT / name
        if not path.is_file():
            continue
        text = original = path.read_text(encoding="utf-8")
        for key, value in values.items():
            text = text.replace("{{" + key + "}}", value)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"  updated {name}")


def set_targets(targets: list[str]) -> None:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    updated, count = re.subn(r"^targets: \[.*\]$", f"targets: [{', '.join(targets)}]", text, flags=re.MULTILINE)
    if count != 1:
        raise HarnessError("harness.config.yaml: expected one line 'targets: [...]'")
    CONFIG_PATH.write_text(updated, encoding="utf-8")
    print(f"  targets: {', '.join(targets)}")


def install_stack(stack: str, assume_yes: bool) -> None:
    if stack == "none":
        print("  no stack.mk installed; `make check` will report 'not implemented' until you add one")
        return
    source = ROOT / "examples" / stack / "stack.mk"
    target = ROOT / "stack.mk"
    if not source.is_file():
        raise HarnessError(f"{rel(source)} not found (was examples/ removed?)")
    if target.exists() and not confirm("stack.mk already exists. Overwrite?", assume_yes):
        print("  kept existing stack.mk")
        return
    shutil.copyfile(source, target)
    print(f"  installed stack.mk from {rel(source)}")


def remove_dir(name: str, flag: bool, assume_yes: bool) -> None:
    path = ROOT / name
    if not path.exists() or not flag:
        return
    if not confirm(f"Delete {name}/ permanently?", assume_yes):
        return
    shutil.rmtree(path)
    print(f"  removed {name}/")
    agents_md = ROOT / "AGENTS.md"
    lines = agents_md.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [line for line in lines if f"]({name}/" not in line]
    if len(kept) != len(lines):
        agents_md.write_text("".join(kept), encoding="utf-8")
        print(f"  removed the {name}/ entry from the AGENTS.md index")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name")
    parser.add_argument("--description")
    parser.add_argument("--owner", help="GitHub user or team for CODEOWNERS/LICENSE, e.g. @my-org/maintainers")
    parser.add_argument("--stack", choices=STACKS)
    parser.add_argument("--targets", help=f"comma-separated subset of {','.join(KNOWN_TARGETS)}")
    parser.add_argument("--remove-examples", action="store_true", help="delete examples/ (asks first)")
    parser.add_argument("--remove-ai", action="store_true", help="delete ai/ (asks first)")
    parser.add_argument("--yes", action="store_true", help="answer yes to confirmations")
    args = parser.parse_args()

    try:
        name = ask("Project name", ROOT.name, args.name)
        description = ask("One-line description", "TODO: describe the project", args.description)
        owner = ask("Code owner (GitHub @user or @org/team)", "@your-github-user", args.owner)
        stack = ask(f"Stack ({'/'.join(STACKS)})", "none", args.stack)
        if stack not in STACKS:
            raise HarnessError(f"unknown stack '{stack}'")
        targets_raw = ask("Targets", ",".join(KNOWN_TARGETS), args.targets)
        targets = [t.strip() for t in targets_raw.split(",") if t.strip()]
        unknown = sorted(set(targets) - set(KNOWN_TARGETS))
        if unknown or not targets:
            raise HarnessError(f"invalid targets {unknown or targets}")

        print("Initialising project:")
        replace_placeholders({
            "PROJECT_NAME": name, "PROJECT_DESCRIPTION": description,
            "PROJECT_OWNER": owner.lstrip("@"), "CODEOWNER": owner,
        })
        set_targets(targets)
        install_stack(stack, args.yes)

        remove_examples = args.remove_examples or (
            args.stack is None and confirm("Remove examples/ (stack samples)?", False))
        remove_ai = args.remove_ai or (
            args.stack is None and confirm("Remove ai/ (only needed if the app calls LLMs)?", False))
        remove_dir("examples", remove_examples, args.yes)
        remove_dir("ai", remove_ai, args.yes)

        history = [p for p in TEMPLATE_HISTORY if (ROOT / p).exists()]
        if history and confirm("Remove the template's own bootstrap plan from docs/plans/completed/?", args.yes):
            for path in history:
                (ROOT / path).unlink()
                print(f"  removed {path}")

        print("Regenerating adapters:")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "harness" / "sync.py"), "--prune",
                                 *(["--yes"] if args.yes else [])], check=False)
        if result.returncode != 0:
            return result.returncode
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("\nNext steps:\n"
          "  1. Review the diff (git diff) and fill docs/architecture/overview.md.\n"
          "  2. Add your toolchain setup to .github/workflows/ci.yml.\n"
          "  3. make harness-lint && make check\n"
          "  4. Replace README.md with your project's README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
