# Stack-agnostic command interface used by humans, agents, hooks and CI.
# Stack commands are defined in stack.mk (copy one from examples/ or run `make harness-init`).
SHELL := bash
.DEFAULT_GOAL := help
PYTHON ?= python3

-include stack.mk

SETUP_CMD          ?=
FMT_CMD            ?=
FMT_CHECK_CMD      ?=
LINT_CMD           ?=
TYPECHECK_CMD      ?=
TEST_CMD           ?=
TEST_FAST_CMD      ?=
BUILD_CMD          ?=
EVAL_CMD           ?=
FMT_FILES_CMD      ?=
FMT_FILES_PATTERNS ?= %

not_implemented = { echo "error: 'make $(1)' is not implemented for this stack. Define $(2) in stack.mk (see examples/README.md)." >&2; exit 1; }
run = $(if $(strip $($(2))),$($(2)),$(call not_implemented,$(1),$(2)))

.PHONY: help setup fmt fmt-check fmt-files lint typecheck test test-fast build check eval \
        harness-deps harness-sync harness-lint harness-gc harness-init

help: ## Show available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install project dependencies
	@$(call run,setup,SETUP_CMD)

fmt: ## Format all source files
	@$(call run,fmt,FMT_CMD)

fmt-check: ## Verify formatting without changing files
	@$(call run,fmt-check,FMT_CHECK_CMD)

FMT_FILES := $(filter $(FMT_FILES_PATTERNS),$(FILES))
fmt-files: ## Format only FILES="a b" (used by hooks; no-op if unsupported)
	@$(if $(and $(strip $(FMT_FILES_CMD)),$(strip $(FMT_FILES))),$(FMT_FILES_CMD) $(FMT_FILES),true)

lint: ## Run linters
	@$(call run,lint,LINT_CMD)

typecheck: ## Run the type checker / compiler
	@$(call run,typecheck,TYPECHECK_CMD)

test: ## Run the full test suite
	@$(call run,test,TEST_CMD)

test-fast: ## Run fast tests (use between edits)
	@$(call run,test-fast,TEST_FAST_CMD)

build: ## Build artifacts
	@$(call run,build,BUILD_CMD)

check: fmt-check lint typecheck test ## Full verification (run before finishing a task)

eval: ## Run LLM evals (see ai/evals/)
	@$(call run,eval,EVAL_CMD)

harness-deps: ## Install harness script dependencies (PyYAML)
	$(PYTHON) -m pip install -r scripts/harness/requirements.txt

harness-sync: ## Generate tool adapters from AGENTS.md + .agents/ (ARGS="--check|--prune")
	@$(PYTHON) scripts/harness/sync.py $(ARGS)

harness-lint: ## Validate the harness (sizes, links, frontmatter, sync, plans)
	@$(PYTHON) scripts/harness/lint.py

harness-gc: ## Report stale plans, unreferenced docs, old TODOs (ARGS="--output file")
	@$(PYTHON) scripts/harness/gc.py $(ARGS)

harness-init: ## Bootstrap a new project from this template
	@$(PYTHON) scripts/harness/init.py $(ARGS)
