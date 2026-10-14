# Plan 0001: Bootstrap the AI harness template

- **Status:** Done
- **Owner:** template maintainers / Claude Code
- **Created:** 2026-10-14 · **Last updated:** 2026-10-14
- **Spec:** [0001-bootstrap-harness.spec.pt-BR.md](0001-bootstrap-harness.spec.pt-BR.md) (original plan, Portuguese)

## Context

Empty repository with only the original plan (`PLAN.md`, now the linked spec). Goal: a tool- and
stack-agnostic template repository demonstrating harness engineering.

## Goal

A GitHub template where `make harness-init` + `make harness-sync` produce a working, verifiable AI-ready project.

## Out of scope

Real application code, runtime multi-agent orchestration, tools without file-based instructions.

## Steps

- [x] 1. Foundation: README, LICENSE, `.gitignore`, `.editorconfig`, CONTRIBUTING, Makefile, `harness.config.yaml`
- [x] 2. Agent contract: `AGENTS.md` (map, < 150 lines), `CLAUDE.md` importing it
- [x] 3. Versioned knowledge: ADR/plan/spec templates, ADR-0001..0003, architecture, conventions, harness docs
- [x] 4. Canonical `.agents/`: 6 skills, 4 subagents, 4 commands, MCP server declarations
- [x] 5. `scripts/harness/sync.py` + adapters for Claude, Copilot, Cursor, Codex, Gemini; hook scripts + Claude wrapper
- [x] 6. `scripts/harness/lint.py`, pre-commit, CI, PR template, CODEOWNERS
- [x] 7. `scripts/harness/gc.py`, weekly GC workflow, learnings log, `harness-retro` skill
- [x] 8. Optional `ai/` module: provider port, prompts, evals
- [x] 9. `scripts/harness/init.py`, `examples/*/stack.mk`, final README

## Acceptance criteria

- [x] `make help` lists all targets; `make check` fails with "not implemented for this stack" without `stack.mk`
- [x] `make harness-lint` passes (sizes, links, frontmatter, sync, plans, hook permissions)
- [x] `make harness-sync` twice → second run writes 0 files
- [x] Hand-editing a generated file makes `make harness-lint` fail
- [x] Removing a target lists orphans and deletes nothing without `--prune` + confirmation
- [x] A staged fake AWS key is blocked by `scripts/hooks/scan-secrets.sh` (pre-commit mode)
- [x] `protect-paths.sh` blocks protected and generated paths (exit 2), via the Claude wrapper too
- [x] `make harness-init ARGS="… --yes"` in a copy, then `make harness-lint` passes
- [ ] CI green on GitHub — pending first push (not verifiable locally)

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Tool config formats change | high | Matrix dated in `docs/harness/adapters.md`; generators isolated per tool in `sync.py` |
| Duplicate skills in Copilot (`.github/skills` + `.claude/skills`) | medium | Documented caveat; drop one target if noisy |

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-10-14 | Python 3 + PyYAML for harness scripts | [ADR-0002](../../adr/0002-python-for-harness-scripts.md) |
| 2026-10-14 | Manifest `.agents/.generated.json` tracks generated files | JSON can't carry headers — [ADR-0003](../../adr/0003-track-generated-files-with-manifest.md) |
| 2026-10-14 | Stack commands live in `stack.mk` (from `examples/`), not in the Makefile | Keeps the Makefile generic; CI skips `make check` with a warning until a stack exists |
| 2026-10-14 | Gemini reads `AGENTS.md` via `context.fileName` instead of a generated `GEMINI.md` | Avoids duplicating the contract |
| 2026-10-14 | No per-phase commits | Repository was not under git; maintainer commits manually |

## Handoff

- **Current state:** all phases implemented and verified locally; repository not yet under git.
- **Next step:** `git init`, first commit, push to GitHub, confirm CI is green, enable *Template repository*,
  replace `OWNER/REPO` in the README badge.
- **Files touched:** whole repository (initial bootstrap).
- **Open questions:** pin GitHub Actions to commit SHAs? Add generators for Cursor/Codex/Gemini subagents once stable.
