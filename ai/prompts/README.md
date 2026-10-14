# Prompts

One file per prompt: `<id>.md`, loaded by `id`. Frontmatter fields:

| Field | Meaning |
|---|---|
| `id` | Stable key used by code (matches the file name) |
| `version` | Semantic version; bump on every change and run `make eval` |
| `model_hint` | `fast` \| `balanced` \| `deep` — mapped to a concrete model by the provider adapter |
| `inputs` | Variables the template expects (`{{name}}`) |
| `output_schema` | Optional JSON Schema file for structured output |

See [summarize-ticket.md](summarize-ticket.md) for an example.
