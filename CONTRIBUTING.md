# Contributing

Humans and AI agents follow the same workflow, described in [AGENTS.md](AGENTS.md).

## Setup

```bash
make harness-deps          # PyYAML for the harness scripts (Python 3.10+)
make setup                 # project dependencies (needs stack.mk)
pipx install pre-commit && pre-commit install
```

## Workflow

1. Non-trivial change? Write a plan from [docs/plans/TEMPLATE.md](docs/plans/TEMPLATE.md) and get it approved.
2. Small commits using [Conventional Commits](docs/conventions/git.md).
3. `make check` and `make harness-lint` before pushing.
4. Open a PR using the template; link the plan.

## Changing the harness

- Edit canonical sources only: [AGENTS.md](AGENTS.md), `.agents/`, `scripts/`, `docs/`.
- Run `make harness-sync` and commit the regenerated adapters together with the source change.
- Never edit generated files (`.claude/`, `.github/{copilot-instructions.md,agents,prompts,skills}`, `.cursor/`,
  `.codex/`, `.gemini/`, `.mcp.json`) — `harness-lint` fails if you do.
- Record non-obvious decisions as ADRs in [docs/adr/](docs/adr/).
- Turn recurring agent mistakes into countermeasures: [docs/harness/learnings.md](docs/harness/learnings.md).
