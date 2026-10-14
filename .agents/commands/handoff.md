---
description: Write a handoff so a new session can resume the current work
argument-hint: "[plan path, optional]"
---

Prepare a handoff for the current work. Plan (if any): $ARGUMENTS

1. Run `git status` and `git diff --stat` to list touched files.
2. Run `make test-fast` and record the result.
3. Update the plan's *Handoff* section: current state, the exact next step, files touched, open questions.
   If there is no plan, print the same four items.
4. Do not start new work.
