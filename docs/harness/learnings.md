# Learnings — the ratchet log

Every recurring agent mistake becomes a countermeasure. Prefer, in order:
**test / lint rule > hook > tool permission > rule text in AGENTS.md or docs**.
Use the [`harness-retro`](../../.agents/skills/harness-retro/SKILL.md) skill to add entries.

| Date | Agent mistake | Root cause | Countermeasure (type: what) | Link |
|---|---|---|---|---|
| 2026-10-14 | Edited a generated adapter instead of its source | Generated files looked like normal files | hook: `protect-paths.sh` blocks generated files; lint: `sync --check` | [ADR-0003](../adr/0003-track-generated-files-with-manifest.md) |
