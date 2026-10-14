#!/usr/bin/env bash
# Formats the given files with the stack formatter (make fmt-files). No-op without stack.mk.
# Usage: format-changed.sh <path>...    Exit 2 = formatter failed (often a syntax error).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

[[ "$#" -gt 0 ]] || exit 0
[[ -f "$ROOT/stack.mk" ]] || exit 0

if ! output="$(make -s --no-print-directory -C "$ROOT" fmt-files FILES="$*" 2>&1)"; then
  echo "Formatting failed for: $*" >&2
  printf '%s\n' "$output" | tail -n 30 >&2
  exit 2
fi
