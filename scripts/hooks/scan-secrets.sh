#!/usr/bin/env bash
# Detects likely secrets. Uses gitleaks when installed, plus built-in patterns.
# Usage: scan-secrets.sh <path>...   scan the given files
#        scan-secrets.sh             scan staged files (pre-commit)
#        scan-secrets.sh --all       scan all tracked files (CI)
# Exit 2 = possible secret found. Allow a false positive with the comment "harness:allow-secret" on that line.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ALLOW_MARKER="harness:allow-secret"

PATTERNS=(
  'aws-access-key:AKIA[0-9A-Z]{16}'
  'private-key:-----BEGIN ([A-Z]+ )?PRIVATE KEY-----'
  'github-token:gh[pousr]_[A-Za-z0-9]{36,}'
  'github-pat:github_pat_[A-Za-z0-9_]{22,}'
  'slack-token:xox[baprs]-[A-Za-z0-9-]{10,}'
  'anthropic-key:sk-ant-[A-Za-z0-9_-]{20,}'
  'openai-key:sk-(proj-)?[A-Za-z0-9_-]{32,}'
  'google-api-key:AIza[0-9A-Za-z_-]{35}'
  'generic-assignment:(api[_-]?key|secret|token|passw(or)?d)["'\'']?[[:space:]]*[:=][[:space:]]*["'\''][^"'\''[:space:]]{16,}["'\'']'
)

files=()
if [[ "${1:-}" == "--all" ]]; then
  mapfile -t files < <(git -C "$ROOT" ls-files)
elif [[ "$#" -eq 0 ]]; then
  mapfile -t files < <(git -C "$ROOT" diff --cached --name-only --diff-filter=ACM)
else
  files=("$@")
fi

found=0
for file in "${files[@]}"; do
  [[ "$file" = /* ]] || file="$ROOT/$file"
  [[ -f "$file" ]] || continue
  for entry in "${PATTERNS[@]}"; do
    name="${entry%%:*}"
    regex="${entry#*:}"
    while IFS= read -r hit; do
      [[ -z "$hit" ]] && continue
      line_no="${hit%%:*}"
      [[ "${hit#*:}" == *"$ALLOW_MARKER"* ]] && continue
      echo "possible secret ($name): ${file#"$ROOT"/}:$line_no" >&2
      found=1
    done < <(grep -nIiE -e "$regex" -- "$file" 2>/dev/null || true)
  done
  if command -v gitleaks >/dev/null 2>&1; then
    if ! gitleaks detect --no-git --no-banner --redact --source "$file" >/dev/null 2>&1; then
      echo "possible secret (gitleaks): ${file#"$ROOT"/}" >&2
      found=1
    fi
  fi
done

if [[ "$found" -ne 0 ]]; then
  echo "Remove the secret (use environment variables) or mark a false positive with '$ALLOW_MARKER'." >&2
  exit 2
fi
