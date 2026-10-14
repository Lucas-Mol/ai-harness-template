---
name: harness-retro
description: Turn an agent mistake into a permanent, preferably deterministic countermeasure (test, lint, hook, permission, or rule) and log it in docs/harness/learnings.md. Use when the agent repeats a mistake, a human corrects the agent, or a review finds an issue an automated check could have caught.
---

# Harness retro (the ratchet)

## 1. Describe the mistake

- What did the agent do? What should it have done? Link the PR/commit/plan.
- Is it recurring, or likely to recur? One-off typos do not need a countermeasure.

## 2. Find the root cause

Ask which part of the harness failed:

| Cause | Typical fix |
|---|---|
| Missing context (didn't know the rule) | doc in `docs/` + link from AGENTS.md index |
| Context ignored (rule exists in text) | make it deterministic: lint/test/hook |
| Missing feedback (nothing failed) | new test, lint rule or `harness-lint` check |
| Tool allowed something dangerous | permission deny rule or `protected_paths` entry |
| Ambiguous procedure | new or improved skill |

## 3. Choose the most deterministic countermeasure

Preference order: **test / lint rule > hook > tool permission > skill > text in AGENTS.md**.
Text in `AGENTS.md` is the last resort — it costs context in every session and can be ignored.

## 4. Implement it

- Canonical sources only (`.agents/`, `scripts/`, `docs/`, `harness.config.yaml` — the latter is protected, so propose the change to a human).
- Prove it works: show the check failing on the old mistake and passing on correct code.
- Run `make harness-sync` and `make harness-lint`.

## 5. Log it

Append a row to `docs/harness/learnings.md`:
`| YYYY-MM-DD | mistake | root cause | type: countermeasure | link |`
