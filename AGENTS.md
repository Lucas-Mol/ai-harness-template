# AGENTS.md — {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

This file is the canonical contract for every AI coding agent working in this repository.
It is a **map**, not an encyclopedia: read the linked docs only when the task needs them.
Tool-specific files (`CLAUDE.md`, `.claude/`, `.github/copilot-instructions.md`, `.cursor/`, `.codex/`, `.gemini/`)
are adapters generated from this file and `.agents/` — never edit them by hand.

## Architecture

- System overview: [docs/architecture/overview.md](docs/architecture/overview.md)
- Layers and dependency rules: [docs/architecture/boundaries.md](docs/architecture/boundaries.md)
- Decisions and their rationale: [docs/adr/](docs/adr/)

## Commands

All work goes through the `Makefile`. Do not call stack tools directly when a target exists.

| Command | When to run |
|---|---|
| `make setup` | Once, after cloning or when dependencies change |
| `make test-fast` | Between edits — the tight feedback loop |
| `make fmt` | After editing source files (hooks may do this for you) |
| `make check` | **Before declaring any task done** (fmt-check + lint + typecheck + test) |
| `make harness-sync` | After changing `AGENTS.md` or anything in `.agents/` |
| `make harness-lint` | After changing docs, skills, agents, commands or plans |
| `make eval` | After changing prompts in `ai/prompts/` (if the project uses LLMs at runtime) |

If a target fails with "not implemented for this stack", report it — do not work around it.

## Workflow

**explore → plan → implement → verify → handoff**

1. **Explore**: read the relevant code and docs before changing anything. Follow existing patterns.
2. **Plan**: non-trivial tasks (more than one module, a new dependency, a schema/API change, or
   more than ~30 minutes of work) need a plan in `docs/plans/active/` from [docs/plans/TEMPLATE.md](docs/plans/TEMPLATE.md).
   Get human approval before implementing it.
3. **Implement**: small, reviewable steps. Run `make test-fast` after each step. Update the plan checklist.
4. **Verify**: `make check` must pass. Add or update tests for every behaviour change.
5. **Handoff**: fill the plan's *Handoff* section (state, next step, files touched). Move finished plans to `docs/plans/completed/`.

Architecture-relevant decisions get an ADR ([docs/adr/0000-template.md](docs/adr/0000-template.md)).

## Rules

- Respect the dependency rules in [docs/architecture/boundaries.md](docs/architecture/boundaries.md).
- Follow [docs/conventions/](docs/conventions/): code style, testing, git, security.
- Prefer simple, readable code over clever code. Match the surrounding style.
- Change only what the task needs. No drive-by refactors; propose them separately.
- Handle errors explicitly. No empty `catch`/`except`.
- Ask before adding a dependency.

## Invariants (never violate)

- **No secrets** in code, config, logs, tests or commits. Use environment variables; see [docs/conventions/security.md](docs/conventions/security.md).
- **Never disable, skip or weaken tests or checks** to make them pass. Fix the cause or ask.
- **Never edit `protected_paths`** listed in [harness.config.yaml](harness.config.yaml) (CI workflows, lock files, `.env*`, the harness config). Ask a human.
- **Never edit generated adapter files.** Change the source in `AGENTS.md` / `.agents/` and run `make harness-sync`.
- **Never delete files or force-push** without explicit human confirmation.

## Definition of Done

- [ ] `make check` passes; `make harness-lint` passes if harness files changed.
- [ ] Tests cover the new or changed behaviour.
- [ ] Docs, ADRs and the plan are updated; the plan's handoff section is filled.
- [ ] The diff contains only changes required by the task.
- [ ] A short summary lists what changed and why, plus anything left undone.

## When you make a mistake

If you hit the same error twice, or a human corrects you, run the `harness-retro` skill:
turn the mistake into a test, lint rule, hook or doc rule and log it in [docs/harness/learnings.md](docs/harness/learnings.md).

## Index

### Docs

- [docs/architecture/](docs/architecture/) — system overview and boundaries
- [docs/adr/](docs/adr/) — Architecture Decision Records
- [docs/plans/](docs/plans/) — execution plans (`active/`, `completed/`, `TEMPLATE.md`)
- [docs/specs/](docs/specs/) — feature specifications (what and why)
- [docs/conventions/](docs/conventions/) — code style, testing, git, security
- [docs/harness/how-it-works.md](docs/harness/how-it-works.md) — how this harness works
- [docs/harness/adapters.md](docs/harness/adapters.md) — tool × feature support matrix
- [docs/harness/learnings.md](docs/harness/learnings.md) — ratchet log: mistake → countermeasure
- [docs/glossary.md](docs/glossary.md) — domain and harness vocabulary
- [ai/README.md](ai/README.md) — runtime LLM module: prompts, evals, providers (optional)

### Skills (`.agents/skills/`)

- `create-plan` — write an execution plan for a non-trivial task
- `execute-plan` — implement an approved plan step by step
- `write-adr` — record an architecture decision
- `code-review` — review a diff against conventions and the plan
- `debug-failing-check` — diagnose a failing `make` target systematically
- `harness-retro` — turn an agent mistake into a deterministic countermeasure

### Subagents (`.agents/agents/`)

- `planner` (read-only) · `implementer` · `reviewer` (read-only) · `security-reviewer` (read-only)
