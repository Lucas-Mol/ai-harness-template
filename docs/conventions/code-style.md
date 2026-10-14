# Code style

Formatting and most style rules are enforced by the stack's formatter and linter (`make fmt`, `make lint`).
This file lists **only** what differs from the language defaults or cannot be automated.

- Names describe intent; avoid abbreviations except well-known ones (`id`, `url`, `http`).
- Comments explain *why*, not *what*. No commented-out code.
- Errors are handled explicitly; never swallow an exception. Add context when re-raising.
- Prefer small functions and early returns over deep nesting.
- No new dependency without approval (see [../../AGENTS.md](../../AGENTS.md)).
- <project-specific rule>
