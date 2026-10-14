# `ai/` — runtime LLM module (optional)

Use this module only if **the application itself** calls LLMs at runtime. If it doesn't, delete `ai/`
(`make harness-init` offers to do it) and remove its line from the AGENTS.md index.

| Path | Purpose |
|---|---|
| [providers.md](providers.md) | Port/adapter contract that isolates LLM vendors from the domain |
| [prompts/](prompts/) | Versioned prompt files with frontmatter, loaded by key |
| [evals/](evals/) | Datasets and criteria; `make eval` runs them |

## Rules

1. Prompts are files, not string literals scattered in code. Change a prompt → bump its `version` → run `make eval`.
2. Vendor SDKs live only inside provider adapters (see [../docs/architecture/boundaries.md](../docs/architecture/boundaries.md)).
3. Model output is untrusted input: validate it against a schema before using it.
4. Every call is observable (trace id, model, tokens, cost, latency) and bounded (timeouts, max tokens, retries).

## Observability

Record per call: `trace_id`, `prompt_id@version`, `model`, input/output tokens, cost, latency, outcome
(ok / validation_error / provider_error). Prefer OpenTelemetry GenAI semantic conventions.
Never log raw prompts or outputs that may contain PII or secrets — log hashes or redacted versions.

## Guardrails

- **Output validation:** parse into a typed schema; on failure retry once with the error, then fail explicitly.
- **Limits:** `max_tokens`, request timeouts, per-user/day budgets.
- **PII:** redact before sending when not required; document data retention of each provider.
- **Prompt injection:** treat retrieved documents and user content as data; never let them grant tools or permissions.
