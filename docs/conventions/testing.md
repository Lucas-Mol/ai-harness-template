# Testing

## Strategy

| Level | Scope | Speed | Run with |
|---|---|---|---|
| Unit | one function/class, no I/O | ms | `make test-fast` |
| Integration | adapters against real dependencies (containers) | seconds | `make test` |
| End-to-end | critical user journeys | minutes | `make test` (or a separate CI job) |
| Evals | LLM behaviour (if applicable) | minutes | `make eval` |

## Rules

- Every behaviour change comes with a test that fails before the change and passes after.
- Bug fixes start with a regression test reproducing the bug.
- Tests are deterministic: no real network, clocks or randomness without control.
- Never delete, skip or loosen a test to make it pass. If a test is wrong, explain why in the PR.
- Test names describe behaviour: `returns_404_when_order_does_not_exist`.
- `make test-fast` must stay under ~30 seconds — it is the agent's inner loop.
