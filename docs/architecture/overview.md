# Architecture overview

> Placeholder. Replace with your system. Keep it to what an agent needs to navigate the code.

## System context (C4 level 1)

```mermaid
flowchart LR
  user([User]) --> system[{{PROJECT_NAME}}]
  system --> ext1[(External system / database)]
  system --> ext2[External API]
```

## Containers (C4 level 2)

```mermaid
flowchart LR
  subgraph system[{{PROJECT_NAME}}]
    api[API / entry points] --> core[Domain core]
    core --> adapters[Adapters: DB, HTTP clients, LLM providers]
  end
  adapters --> db[(Database)]
```

## Where things live

| Concern | Path |
|---|---|
| Entry points | `<path>` |
| Domain logic | `<path>` |
| Adapters / infrastructure | `<path>` |
| Tests | `<path>` |
