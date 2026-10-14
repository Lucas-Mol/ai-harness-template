# Stack examples

The root [Makefile](../Makefile) defines a stack-agnostic interface. Each project implements it in a
`stack.mk` file at the repository root by setting these variables:

| Variable | Target | Expectation |
|---|---|---|
| `SETUP_CMD` | `make setup` | install dependencies reproducibly (lock file) |
| `FMT_CMD` / `FMT_CHECK_CMD` | `make fmt` / `make fmt-check` | format / verify formatting |
| `LINT_CMD` | `make lint` | static analysis, including architecture rules |
| `TYPECHECK_CMD` | `make typecheck` | type checker or compiler |
| `TEST_CMD` | `make test` | full suite |
| `TEST_FAST_CMD` | `make test-fast` | < ~30 s, used by agents between edits and by the Stop hook |
| `BUILD_CMD` | `make build` | build artifacts |
| `EVAL_CMD` | `make eval` | LLM evals (only with the optional `ai/` module) |
| `FMT_FILES_CMD` + `FMT_FILES_PATTERNS` | `make fmt-files FILES=…` | format single files after an agent edit (optional) |

Unset variables make the target fail with "not implemented for this stack" — explicit, never silently green.

## Ready-made stack files

| Stack | File | Tools |
|---|---|---|
| Java | [java/stack.mk](java/stack.mk) | Maven wrapper (Gradle in comments), Spotless, Checkstyle |
| Python | [python/stack.mk](python/stack.mk) | uv, ruff, mypy, pytest |
| Node.js | [node/stack.mk](node/stack.mk) | pnpm, prettier, eslint, tsc, vitest |
| Go | [go/stack.mk](go/stack.mk) | gofmt, golangci-lint, go test |

Use one with `make harness-init` (asks for the stack) or manually: `cp examples/python/stack.mk stack.mk`.
Then add the toolchain setup step to [.github/workflows/ci.yml](../.github/workflows/ci.yml)
(`actions/setup-java`, `astral-sh/setup-uv`, `pnpm/action-setup` + `actions/setup-node`, `actions/setup-go`).

## Tips

- Mark slow tests (`@pytest.mark.slow`, JUnit `@Tag("slow")`, `testing.Short()`) so `test-fast` stays fast.
- Put architecture rules in `LINT_CMD` (import-linter, dependency-cruiser, ArchUnit tests, depguard).
- Monorepo? `stack.mk` may call sub-makefiles: `TEST_CMD = $(MAKE) -C backend test && $(MAKE) -C web test`.
