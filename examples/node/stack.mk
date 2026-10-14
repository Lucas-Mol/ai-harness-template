# Node.js / TypeScript with pnpm, prettier, eslint, tsc and vitest.
SETUP_CMD          = pnpm install --frozen-lockfile
FMT_CMD            = pnpm exec prettier --write .
FMT_CHECK_CMD      = pnpm exec prettier --check .
LINT_CMD           = pnpm exec eslint .
TYPECHECK_CMD      = pnpm exec tsc --noEmit
TEST_CMD           = pnpm exec vitest run
TEST_FAST_CMD      = pnpm exec vitest run --changed
BUILD_CMD          = pnpm run build
FMT_FILES_CMD      = pnpm exec prettier --write --ignore-unknown
FMT_FILES_PATTERNS = %.ts %.tsx %.js %.jsx %.json %.css %.md
# EVAL_CMD         = pnpm exec promptfoo eval
