# Evals

Datasets are JSONL files: one case per line, named `<prompt-id>.jsonl`.

```json
{"id": "case-1", "input": {"ticket_title": "...", "ticket_body": "..."}, "expected": "...", "rubric": ["..."], "tags": ["regression"]}
```

| Field | Meaning |
|---|---|
| `id` | Stable case id |
| `input` | Values for the prompt's `inputs` |
| `expected` | Optional exact/reference answer (for deterministic graders) |
| `rubric` | Criteria for model-graded or human evaluation |
| `tags` | e.g. `regression`, `edge-case`, `safety` |

## Running

Implement `EVAL_CMD` in `stack.mk` with your stack's eval runner (e.g. promptfoo, a pytest/JUnit suite, or a small script).
The runner must print a per-case result and **exit non-zero when the pass rate drops below the threshold**
so that, once enabled in CI, an eval regression breaks the build.

Every production bug caused by a prompt becomes a new `regression` case (the ratchet, applied to prompts).
