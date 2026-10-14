# Python with uv (https://docs.astral.sh/uv/), ruff, mypy and pytest.
SETUP_CMD          = uv sync --all-groups
FMT_CMD            = uv run ruff format . && uv run ruff check --fix .
FMT_CHECK_CMD      = uv run ruff format --check .
LINT_CMD           = uv run ruff check .
TYPECHECK_CMD      = uv run mypy .
TEST_CMD           = uv run pytest
TEST_FAST_CMD      = uv run pytest -x -q -m "not slow"
BUILD_CMD          = uv build
FMT_FILES_CMD      = uv run ruff format
FMT_FILES_PATTERNS = %.py
# EVAL_CMD         = uv run pytest evals/ -q
