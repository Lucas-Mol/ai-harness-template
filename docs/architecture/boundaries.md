# Boundaries and dependency rules

> Default: hexagonal (ports & adapters). Adjust to your project and **enforce with a tool** where possible
> (ArchUnit, import-linter, dependency-cruiser, depguard).

## Layers

| Layer | Contains | May depend on |
|---|---|---|
| `domain` | entities, value objects, domain services, **ports** (interfaces) | nothing outside `domain` |
| `application` | use cases orchestrating the domain | `domain` |
| `adapters` | DB, HTTP, messaging, LLM providers implementing ports | `application`, `domain`, external libs |
| `entrypoints` | HTTP handlers, CLI, jobs; wiring/DI | everything above |

## Rules

1. Dependencies point inwards: `entrypoints → adapters → application → domain`.
2. Framework, SDK and vendor types never appear in `domain` or `application` signatures.
3. LLM provider SDKs live only in their adapter (see `ai/providers.md` when the optional `ai/` module is used).
4. Cross-module access goes through the public API of the module, not its internals.
5. A new rule here should come with an automated check, otherwise it will drift.

## Enforcement

| Rule | Check | Command |
|---|---|---|
| <rule> | <tool / test> | `make lint` |
