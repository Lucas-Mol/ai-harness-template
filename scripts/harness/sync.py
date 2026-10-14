#!/usr/bin/env python3
"""Generate tool adapters from AGENTS.md + .agents/ for every target in harness.config.yaml.

Usage:
  sync.py            write adapters (idempotent)
  sync.py --check    exit 1 if any adapter is missing, stale, hand-edited or orphaned
  sync.py --prune    delete orphaned generated files after confirmation (--yes skips the prompt)

See docs/harness/adapters.md for what each target receives and why.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from common import (
    AGENTS_DIR,
    GENERATED_MARKER,
    KNOWN_TARGETS,
    MANIFEST_PATH,
    ROOT,
    HarnessError,
    dump_frontmatter,
    load_config,
    load_yaml,
    rel,
    split_frontmatter,
)

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ARGS_TOKEN = "$ARGUMENTS"
RELATIVE_LINK_RE = re.compile(r"\]\((?!https?://|mailto:|#|/)([^)\s]+)\)")


@dataclass(frozen=True)
class Doc:
    """A canonical markdown source with frontmatter (skill, agent or command)."""

    name: str
    meta: dict[str, Any]
    body: str
    source: str
    extra_files: dict[str, bytes] = field(default_factory=dict)


@dataclass(frozen=True)
class Sources:
    config: dict[str, Any]
    agents_md: str
    skills: list[Doc]
    agents: list[Doc]
    commands: list[Doc]
    mcp_servers: dict[str, dict[str, Any]]


# --------------------------------------------------------------------------- loading


def _checked_name(name: str, source: Path) -> str:
    if not NAME_RE.match(name):
        raise HarnessError(f"{rel(source)}: name '{name}' must be lowercase kebab-case")
    return name


def _load_doc(path: Path, name: str) -> Doc:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"), path)
    return Doc(name=_checked_name(name, path), meta=meta, body=body, source=rel(path))


def load_skills() -> list[Doc]:
    skills = []
    for skill_md in sorted((AGENTS_DIR / "skills").glob("*/SKILL.md")):
        skill_dir = skill_md.parent
        doc = _load_doc(skill_md, skill_dir.name)
        extras = {
            p.relative_to(skill_dir).as_posix(): p.read_bytes()
            for p in sorted(skill_dir.rglob("*"))
            if p.is_file() and p != skill_md and "__pycache__" not in p.parts
        }
        skills.append(Doc(doc.name, doc.meta, doc.body, doc.source, extras))
    return skills


def load_docs(subdir: str) -> list[Doc]:
    return [_load_doc(p, p.stem) for p in sorted((AGENTS_DIR / subdir).glob("*.md"))]


def load_mcp_servers() -> dict[str, dict[str, Any]]:
    path = AGENTS_DIR / "mcp" / "servers.yaml"
    if not path.is_file():
        return {}
    data = load_yaml(path) or {}
    servers = data.get("servers") or {}
    if not isinstance(servers, dict):
        raise HarnessError(f"{rel(path)}: 'servers' must be a mapping")
    enabled = {}
    for name, server in servers.items():
        if not isinstance(server, dict) or not server.get("enabled", False):
            continue
        kind = server.get("type")
        if kind == "stdio" and not server.get("command"):
            raise HarnessError(f"{rel(path)}: server '{name}' (stdio) needs 'command'")
        if kind == "http" and not server.get("url"):
            raise HarnessError(f"{rel(path)}: server '{name}' (http) needs 'url'")
        if kind not in ("stdio", "http"):
            raise HarnessError(f"{rel(path)}: server '{name}' has invalid type '{kind}'")
        enabled[name] = server
    return enabled


def load_sources() -> Sources:
    config = load_config()
    targets = config.get("targets") or []
    unknown = sorted(set(targets) - set(KNOWN_TARGETS))
    if unknown:
        raise HarnessError(f"harness.config.yaml: unknown targets {unknown}; known: {list(KNOWN_TARGETS)}")
    return Sources(
        config=config,
        agents_md=(ROOT / "AGENTS.md").read_text(encoding="utf-8"),
        skills=load_skills(),
        agents=load_docs("agents"),
        commands=load_docs("commands"),
        mcp_servers=load_mcp_servers(),
    )


# --------------------------------------------------------------------------- rendering helpers


def md_header(source: str) -> str:
    return f"<!-- {GENERATED_MARKER}. Source: {source} -->\n"


def render_md(meta: dict[str, Any] | None, source: str, body: str) -> bytes:
    frontmatter = dump_frontmatter(meta) if meta else ""
    return (frontmatter + md_header(source) + body).encode("utf-8")


def render_json(data: Any) -> bytes:
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def toml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_multiline(value: str) -> str:
    if "'''" not in value:
        return f"'''\n{value}'''"
    escaped = value.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped}"""'


def skill_files(prefix: str, skills: list[Doc]) -> dict[str, bytes]:
    out = {}
    for skill in skills:
        out[f"{prefix}/{skill.name}/SKILL.md"] = render_md(skill.meta, skill.source, skill.body)
        for name, content in skill.extra_files.items():
            out[f"{prefix}/{skill.name}/{name}"] = content
    return out


def mapped_tools(agent: Doc, mapping: dict[str, list[str]]) -> list[str]:
    tools: list[str] = []
    for abstract in agent.meta.get("tools") or []:
        for tool in mapping.get(abstract, []):
            if tool not in tools:
                tools.append(tool)
    return tools


def command_meta(command: Doc, keys: tuple[str, ...]) -> dict[str, Any]:
    return {k: command.meta[k] for k in keys if k in command.meta}


def mcp_env_refs(server: dict[str, Any], ref: Callable[[str], str]) -> dict[str, str]:
    return {name: ref(name) for name in server.get("env") or []}


def mcp_json_servers(servers: dict[str, dict[str, Any]], ref: Callable[[str], str],
                     http_url_key: str = "url", http_type: str | None = "http") -> dict[str, Any]:
    """Translate servers into the common `mcpServers` JSON shape, with per-tool env var syntax."""
    result: dict[str, Any] = {}
    for name, server in servers.items():
        if server["type"] == "stdio":
            entry: dict[str, Any] = {"command": server["command"], "args": list(server.get("args") or [])}
            env = mcp_env_refs(server, ref)
            if env:
                entry["env"] = env
        else:
            entry = {"type": http_type} if http_type else {}
            entry[http_url_key] = server["url"]
            token_env = server.get("bearer_token_env")
            if token_env:
                entry["headers"] = {"Authorization": f"Bearer {ref(token_env)}"}
        result[name] = entry
    return result


# --------------------------------------------------------------------------- targets

CLAUDE_TOOLS = {"read": ["Read", "Grep", "Glob"], "write": ["Edit", "Write"], "shell": ["Bash"],
                "web": ["WebFetch", "WebSearch"]}
CLAUDE_MODELS = {"fast": "haiku", "balanced": "sonnet", "deep": "opus"}
CLAUDE_EDIT_TOOLS = "Edit|MultiEdit|Write|NotebookEdit"


def claude_hook(hook: str, timeout: int | None = None) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "type": "command",
        "command": f'python3 "$CLAUDE_PROJECT_DIR/scripts/hooks/wrappers/claude.py" {hook}',
    }
    if timeout:
        entry["timeout"] = timeout
    return entry


def claude_settings(config: dict[str, Any]) -> dict[str, Any]:
    deny = [f"Read(./{p})" for p in config.get("secret_files") or []]
    deny += [f"Bash({c}:*)" for c in config.get("deny_commands") or []]
    return {
        "$schema": "https://json.schemastore.org/claude-code-settings.json",
        "permissions": {"deny": deny},
        "hooks": {
            "PreToolUse": [{"matcher": CLAUDE_EDIT_TOOLS, "hooks": [claude_hook("protect-paths")]}],
            "PostToolUse": [{"matcher": CLAUDE_EDIT_TOOLS,
                             "hooks": [claude_hook("format-changed"), claude_hook("scan-secrets")]}],
            "Stop": [{"hooks": [claude_hook("check-on-stop", timeout=600)]}],
        },
    }


def build_claude(src: Sources) -> dict[str, bytes]:
    out = skill_files(".claude/skills", src.skills)
    for agent in src.agents:
        meta: dict[str, Any] = {"name": agent.name, "description": agent.meta.get("description", "")}
        tools = mapped_tools(agent, CLAUDE_TOOLS)
        if tools:
            meta["tools"] = ", ".join(tools)
        model = CLAUDE_MODELS.get(agent.meta.get("model_hint", ""))
        if model:
            meta["model"] = model
        out[f".claude/agents/{agent.name}.md"] = render_md(meta, agent.source, agent.body)
    for command in src.commands:
        meta = command_meta(command, ("description", "argument-hint"))
        out[f".claude/commands/{command.name}.md"] = render_md(meta, command.source, command.body)
    out[".claude/settings.json"] = render_json(claude_settings(src.config))
    if src.mcp_servers:
        servers = mcp_json_servers(src.mcp_servers, lambda v: "${" + v + "}")
        out[".mcp.json"] = render_json({"mcpServers": servers})
    return out


COPILOT_TOOLS = {"read": ["read", "search"], "write": ["edit"], "shell": ["execute"], "web": ["web"]}


def build_copilot(src: Sources) -> dict[str, bytes]:
    # copilot-instructions.md lives in .github/, so relative links need one more "../".
    instructions = RELATIVE_LINK_RE.sub(lambda m: f"](../{m.group(1)})", src.agents_md)
    out = {".github/copilot-instructions.md": render_md(None, "AGENTS.md", instructions)}
    out.update(skill_files(".github/skills", src.skills))
    for agent in src.agents:
        meta: dict[str, Any] = {"name": agent.name, "description": agent.meta.get("description", "")}
        tools = mapped_tools(agent, COPILOT_TOOLS)
        if tools:
            meta["tools"] = tools
        out[f".github/agents/{agent.name}.agent.md"] = render_md(meta, agent.source, agent.body)
    for command in src.commands:
        meta = command_meta(command, ("description", "argument-hint"))
        body = command.body.replace(ARGS_TOKEN, "${input:args}")
        out[f".github/prompts/{command.name}.prompt.md"] = render_md(meta, command.source, body)
    return out


def build_cursor(src: Sources) -> dict[str, bytes]:
    # Cursor reads AGENTS.md natively; no rule file is needed.
    out = skill_files(".cursor/skills", src.skills)
    for command in src.commands:
        body = command.body.replace(ARGS_TOKEN, "the text provided after the command").lstrip("\n")
        out[f".cursor/commands/{command.name}.md"] = render_md(None, command.source, body)
    if src.mcp_servers:
        servers = mcp_json_servers(src.mcp_servers, lambda v: "${env:" + v + "}", http_type=None)
        out[".cursor/mcp.json"] = render_json({"mcpServers": servers})
    return out


def build_codex(src: Sources) -> dict[str, bytes]:
    # Codex reads AGENTS.md and .agents/skills natively; only MCP needs a project config.
    if not src.mcp_servers:
        return {}
    lines = [f"# {GENERATED_MARKER}. Source: .agents/mcp/servers.yaml", ""]
    for name, server in src.mcp_servers.items():
        lines.append(f"[mcp_servers.{toml_str(name)}]")
        if server["type"] == "stdio":
            lines.append(f"command = {toml_str(server['command'])}")
            lines.append(f"args = [{', '.join(toml_str(a) for a in server.get('args') or [])}]")
            if server.get("env"):
                lines.append(f"env_vars = [{', '.join(toml_str(e) for e in server['env'])}]")
        else:
            lines.append(f"url = {toml_str(server['url'])}")
            if server.get("bearer_token_env"):
                lines.append(f"bearer_token_env_var = {toml_str(server['bearer_token_env'])}")
        lines.append("")
    return {".codex/config.toml": "\n".join(lines).encode("utf-8")}


def build_gemini(src: Sources) -> dict[str, bytes]:
    # Gemini CLI reads .agents/skills natively (alias of .gemini/skills).
    settings: dict[str, Any] = {"context": {"fileName": ["AGENTS.md"]}}
    if src.mcp_servers:
        settings["mcpServers"] = mcp_json_servers(src.mcp_servers, lambda v: "$" + v,
                                                  http_url_key="httpUrl", http_type=None)
    out = {".gemini/settings.json": render_json(settings)}
    for command in src.commands:
        prompt = command.body.replace(ARGS_TOKEN, "{{args}}").lstrip("\n")
        toml = (
            f"# {GENERATED_MARKER}. Source: {command.source}\n"
            f"description = {toml_str(str(command.meta.get('description', '')))}\n"
            f"prompt = {toml_multiline(prompt)}\n"
        )
        out[f".gemini/commands/{command.name}.toml"] = toml.encode("utf-8")
    return out


BUILDERS: dict[str, Callable[[Sources], dict[str, bytes]]] = {
    "claude": build_claude,
    "copilot": build_copilot,
    "cursor": build_cursor,
    "codex": build_codex,
    "gemini": build_gemini,
}


def compute_outputs(src: Sources) -> dict[str, bytes]:
    outputs: dict[str, bytes] = {}
    for target in src.config.get("targets") or []:
        for path, content in BUILDERS[target](src).items():
            if path in outputs and outputs[path] != content:
                raise HarnessError(f"two targets generate different content for {path}")
            outputs[path] = content
    return dict(sorted(outputs.items()))


# --------------------------------------------------------------------------- manifest & io


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        return {"files": {}, "orphans": []}
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HarnessError(f"{rel(MANIFEST_PATH)}: invalid JSON ({exc}); delete it and re-run sync") from exc


def render_manifest(outputs: dict[str, bytes], orphans: list[str]) -> bytes:
    return render_json({
        "note": f"{GENERATED_MARKER}. Generated adapter files and their SHA-256 (see ADR-0003).",
        "files": {path: sha256(content) for path, content in outputs.items()},
        "orphans": orphans,
    })


def find_orphans(outputs: dict[str, bytes]) -> list[str]:
    manifest = load_manifest()
    previous = set(manifest.get("files", {})) | set(manifest.get("orphans", []))
    return sorted(p for p in previous - set(outputs) if (ROOT / p).exists())


def check(outputs: dict[str, bytes], orphans: list[str]) -> int:
    problems = []
    for path, content in outputs.items():
        target = ROOT / path
        if not target.is_file():
            problems.append(f"missing: {path}")
        elif target.read_bytes() != content:
            problems.append(f"stale or hand-edited: {path}")
    problems += [f"orphaned (target removed?): {p}" for p in orphans]
    if not MANIFEST_PATH.is_file() or MANIFEST_PATH.read_bytes() != render_manifest(outputs, orphans):
        problems.append(f"stale: {rel(MANIFEST_PATH)}")
    if problems:
        print("Adapters are out of sync with AGENTS.md / .agents/:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print("Edit the canonical sources, then run `make harness-sync`"
              + (" (orphans: `make harness-sync ARGS=--prune`)." if orphans else "."), file=sys.stderr)
        return 1
    print(f"Adapters in sync ({len(outputs)} files).")
    return 0


def confirm(question: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print(f"{question} — not a terminal; re-run with --yes to confirm.", file=sys.stderr)
        return False
    return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def remove_empty_parents(path: Path) -> None:
    parent = path.parent
    while parent != ROOT and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()
        parent = parent.parent


def write(outputs: dict[str, bytes], orphans: list[str], prune: bool, assume_yes: bool) -> int:
    written = 0
    for path, content in outputs.items():
        target = ROOT / path
        if target.is_file() and target.read_bytes() == content:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        written += 1
        print(f"  wrote {path}")

    if orphans:
        print("Orphaned generated files (no longer produced by any target):")
        for path in orphans:
            print(f"  - {path}")
        if prune and confirm(f"Delete these {len(orphans)} files?", assume_yes):
            for path in orphans:
                (ROOT / path).unlink()
                remove_empty_parents(ROOT / path)
                print(f"  deleted {path}")
            orphans = []
        elif not prune:
            print("Kept. Run `make harness-sync ARGS=--prune` to delete them.")

    manifest = render_manifest(outputs, orphans)
    if not MANIFEST_PATH.is_file() or MANIFEST_PATH.read_bytes() != manifest:
        MANIFEST_PATH.write_bytes(manifest)
        written += 1
    print(f"Sync done: {written} file(s) written, {len(outputs)} generated in total.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify only; exit 1 on drift")
    parser.add_argument("--prune", action="store_true", help="delete orphaned generated files")
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation when pruning")
    args = parser.parse_args()
    try:
        outputs = compute_outputs(load_sources())
        orphans = find_orphans(outputs)
        if args.check:
            return check(outputs, orphans)
        return write(outputs, orphans, args.prune, args.yes)
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
