---
description: Review the current changes against plan, conventions and boundaries
argument-hint: "[base branch, PR or path; default: main]"
---

Review the changes for: $ARGUMENTS (default: `git diff main...HEAD` plus uncommitted changes).

Use the `code-review` skill. If the changes touch input handling, auth, secrets, dependencies or LLM calls,
also apply the `security-reviewer` checklist. Do not edit files. Output findings ordered by severity.
