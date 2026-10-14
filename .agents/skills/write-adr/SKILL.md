---
name: write-adr
description: Record an Architecture Decision Record in docs/adr/. Use when choosing between technical options with lasting impact (framework, storage, protocol, layering, dependency, harness change) or when the user asks to document a decision.
---

# Write an ADR

1. Next number: highest `docs/adr/NNNN-*.md` + 1.
2. Copy `docs/adr/0000-template.md` to `docs/adr/NNNN-short-imperative-title.md`.
3. Fill it:
   - **Context**: facts and forces only — no solution yet.
   - **Decision drivers**: the criteria the options are judged by.
   - **Considered options**: at least two real options, including "do nothing" when plausible.
   - **Decision**: "We will …, because …" tied to the drivers.
   - **Consequences**: positive, negative (what we accept) and follow-ups.
4. Status starts as **Proposed**. Only a human sets **Accepted**.
5. If it replaces an ADR, set the old one to "Superseded by ADR-NNNN" — do not rewrite its content.
6. Add the ADR to the table in `docs/adr/README.md`.
7. If the decision implies a rule, add a check for it (lint, test, hook) or a follow-up step in the plan.
8. Run `make harness-lint`.
