# Glossary

## Harness

| Term | Meaning |
|---|---|
| **Harness** | Everything around the model that makes an agent effective and safe: context, tools, constraints, feedback loops, verification. |
| **Adapter** | A tool-specific file generated from the canonical sources (e.g. `.claude/settings.json`). |
| **Backpressure** | Deterministic checks the agent runs to validate its own work (`make test-fast`, `make check`). |
| **Guardrail** | A rule enforced by code (hook, lint, CI, permission) rather than by prompt text. |
| **Progressive disclosure** | Keep the always-loaded context small (`AGENTS.md`); load details from `docs/` on demand. |
| **Ratchet** | Each recurring agent mistake becomes a permanent countermeasure; quality only moves one way. |
| **Garbage collection** | Periodic detection of stale plans, unreferenced docs and old TODOs (`make harness-gc`). |
| **Skill** | An on-demand procedure in `SKILL.md` format, loaded when its `description` matches the task. |
| **Subagent** | A role with a restricted toolset and its own context window (planner, reviewer…). |
| **Handoff** | The section of a plan that lets a fresh session resume work. |

## Domain

| Term | Meaning |
|---|---|
| <term> | <definition> |
