# ADR-0001: Adopt AGENTS.md + `.agents/` as the single source of truth

- **Status:** Accepted
- **Date:** 2026-10-14
- **Deciders:** template maintainers

## Context

Every AI coding tool reads its own instruction files: `CLAUDE.md` and `.claude/` (Claude Code),
`.github/copilot-instructions.md` (Copilot), `.cursor/` (Cursor), `.gemini/` (Gemini CLI), `.codex/` (Codex).
Maintaining the same rules in several places drifts quickly, and teams use more than one tool.

Open standards now exist: [AGENTS.md](https://agents.md) for instructions and
[Agent Skills](https://agentskills.io) (`SKILL.md`) for on-demand procedures. Several tools read them natively.

## Decision drivers

- One place to change a rule.
- Not locked to a single vendor.
- Works on Windows without symlinks.
- Each tool still gets its native features (hooks, permissions, slash commands).

## Considered options

1. Maintain each tool's files by hand.
2. Symlink tool files to a shared source.
3. Keep canonical, tool-neutral sources and **generate** tool adapters with a sync script.

## Decision

We adopt option 3. `AGENTS.md` and `.agents/` (skills, agents, commands, MCP servers) are canonical.
`scripts/harness/sync.py` generates every adapter listed in `harness.config.yaml: targets`.
`CLAUDE.md` is the only hand-written adapter: it just imports `@AGENTS.md`.

## Consequences

- **Positive:** single source; adding a tool is a new generator function; open standards first.
- **Negative:** contributors must run `make harness-sync`; generated files are committed (so tools work right after clone).
- **Follow-ups:** `harness-lint` fails when adapters drift (`sync --check`); hooks block hand edits to generated files.
