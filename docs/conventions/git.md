# Git

## Commits

[Conventional Commits](https://www.conventionalcommits.org/): `type(scope): imperative summary`.

- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`, `build`.
- Summary in English, imperative, ≤ 72 characters: `fix(parser): handle empty input`.
- One logical change per commit. Explain *why* in the body when it is not obvious.
- Agent-authored commits keep the tool's co-author trailer.

## Branches

- `main` is always releasable and protected.
- Short-lived branches: `type/short-description` (e.g. `feat/order-export`).

## Pull requests

- Small: aim for < 400 changed lines. Split larger work using the plan's steps.
- Use [the PR template](../../.github/pull_request_template.md): link the plan, tick the Definition of Done.
- CI must be green. Changes to protected paths need a CODEOWNERS review.
- Never `git push --force` to shared branches; use `--force-with-lease` on your own branch only.
