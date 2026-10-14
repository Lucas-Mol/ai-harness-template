# LLM provider port (hexagonal)

The domain and application layers depend on this **port**, never on a vendor SDK.
Each provider (Anthropic, OpenAI, Google, local models…) is an **adapter** in the adapters layer.

## Port

Pseudocode — implement it in your language with your own types:

```text
interface LlmProvider {
  complete(request: CompletionRequest) -> CompletionResult
  stream(request: CompletionRequest) -> Stream<CompletionChunk>
  embed(texts: list<string>, model_hint: ModelHint) -> list<Vector>
  tool_call(request: CompletionRequest, tools: list<ToolSpec>) -> ToolCallResult
}

CompletionRequest {
  prompt_id: string            # key in ai/prompts/, e.g. "summarize-ticket"
  prompt_version: string
  messages: list<Message>      # rendered from the prompt file + inputs
  model_hint: fast | balanced | deep
  max_tokens: int
  temperature: float?
  response_schema: Schema?     # when structured output is expected
  timeout: Duration
  metadata: { trace_id, user_id_hash, ... }
}

CompletionResult {
  text: string
  parsed: object?              # validated against response_schema
  usage: { input_tokens, output_tokens, cost }
  model: string                # concrete model actually used
  latency: Duration
  finish_reason: stop | length | tool_use | content_filter | error
}
```

## Rules

- `model_hint` is mapped to concrete model ids **inside the adapter** (configurable), so upgrading models is a config change.
- Adapters translate vendor errors into a small set of domain errors: `RateLimited`, `Timeout`, `InvalidRequest`,
  `ProviderUnavailable`, `OutputValidationFailed`.
- Retries with backoff live in the adapter; idempotency is the caller's decision.
- A fake/in-memory adapter exists for tests; unit tests never call a real provider.
- Evals (`make eval`) run against the real adapter, selected by configuration.
