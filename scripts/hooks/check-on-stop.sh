#!/usr/bin/env bash
# Runs fast checks when an agent is about to finish. Exit 2 = checks failed (the agent should keep working).
# Usage: check-on-stop.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

run_check() {
  local target="$1" output
  if ! output="$(make -s --no-print-directory -C "$ROOT" "$target" 2>&1)"; then
    echo "'make $target' failed. Fix it before finishing (do not skip or weaken checks):" >&2
    printf '%s\n' "$output" | tail -n 40 >&2
    return 1
  fi
}

failed=0
run_check harness-lint || failed=1
if [[ -f "$ROOT/stack.mk" ]]; then
  run_check test-fast || failed=1
fi

[[ "$failed" -eq 0 ]] || exit 2
