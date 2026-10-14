---
name: create-plan
description: Write an execution plan in docs/plans/active/ before implementing. Use when a task touches more than one module, adds a dependency, changes a schema or public API, or will take more than ~30 minutes — or when the user asks for a plan.
---

# Create an execution plan

## Steps

1. **Explore first.** Read the relevant code, [AGENTS.md](../../../AGENTS.md), the architecture docs and any spec.
   Do not change code during this skill.
2. **Pick the number.** Next free `NNNN` across `docs/plans/active/` and `docs/plans/completed/`.
3. **Copy the template.** `docs/plans/TEMPLATE.md` → `docs/plans/active/NNNN-short-title.md`.
4. **Fill every section:**
   - *Context*: what exists today, with file paths you read.
   - *Goal*: observable outcome in 1–2 sentences.
   - *Out of scope*: what you will deliberately not do.
   - *Steps*: checkboxes, each small enough to verify with `make test-fast`. The last step is `make check`.
   - *Acceptance criteria*: each one verifiable by a command and its expected output.
   - *Risks*, *Decision log*, *Handoff* (status: "Draft, awaiting approval").
5. **Flag decisions.** If a step needs an architecture decision, add a step to write an ADR (`write-adr` skill).
6. **Validate.** Run `make harness-lint`.
7. **Stop and ask for approval.** Summarise the plan in ≤ 10 lines. Do not implement until a human approves.

## Quality bar

- A new session could execute the plan using only the plan and the repo.
- No vague steps such as "improve X" or "refactor as needed".
- Unknowns are written as open questions, not guesses.
