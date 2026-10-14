# PLAN.md — ai-harness-template

> Plano de execução para o agente de código (Claude Code ou equivalente) construir um **template de repositório com AI Harness**, agnóstico de ferramenta e de stack, para ser publicado no GitHub como *Template Repository* e reutilizado em projetos futuros.

---

## 0. Instruções para o agente que vai executar este plano

1. Execute **uma fase por vez**, na ordem. Ao fim de cada fase: rode os critérios de aceite, faça **um commit** (Conventional Commits) e pare para revisão humana.
2. **Nunca remova arquivos ou pastas sem pedir permissão explícita.**
3. Antes de escrever qualquer arquivo de configuração específico de ferramenta (Claude Code, Codex, Copilot, Cursor, Gemini CLI), **consulte a documentação oficial atual** dessa ferramenta. Formatos de hooks, skills e MCP mudam com frequência; não confie em memória.
4. Não invente stack: o template é **agnóstico de linguagem**. Onde houver código de aplicação, use apenas exemplos mínimos em `examples/`.
5. Todo conteúdo do repositório gerado (README, docs, comentários) em **inglês**. Este PLAN.md fica em português.
6. Evite symlinks (quebram no Windows/Git sem configuração). Use **scripts de sincronização** que copiam/geram arquivos.
7. Mantenha o progresso em `docs/plans/active/0001-bootstrap-harness.md` (checklist), atualizado a cada fase.

---

## 1. Objetivo e princípios

**Objetivo:** um esqueleto que mostre toda a arquitetura de um projeto orientado a IA com boas práticas de *harness engineering*: contexto, restrições, ferramentas, feedback loops, verificação e manutenção contra entropia.

**Princípios de design:**

| Princípio | Como se materializa |
|---|---|
| **Fonte única da verdade** | Tudo canônico em `AGENTS.md` + `.agents/`. Arquivos de cada ferramenta são *adapters* gerados. |
| **Agnóstico de ferramenta** | Padrões abertos primeiro (AGENTS.md, Agent Skills/`SKILL.md`, MCP). Claude é só um dos adapters. |
| **Agnóstico de stack** | Interface de comandos padronizada (`make check`, `make test`…) que cada projeto implementa. |
| **Progressive disclosure** | `AGENTS.md` curto (mapa), detalhes em `docs/` carregados sob demanda. |
| **Backpressure / feedback loops** | Agente valida o próprio trabalho via comandos determinísticos (lint, tipos, testes, harness-lint). |
| **Guardrails determinísticos** | Regras que importam são aplicadas por scripts/hooks/CI, não só por texto em prompt. |
| **Ratchet** | Todo erro recorrente do agente vira regra, teste, lint ou hook (registrado em `docs/harness/learnings.md`). |
| **Garbage collection** | Checagens periódicas de docs/planos obsoletos, links quebrados e tamanho de contexto. |

---

## 2. Estrutura alvo

```
ai-harness-template/
├── AGENTS.md                      # Contrato canônico do agente (mapa, comandos, regras, invariantes)
├── CLAUDE.md                      # Adapter: contém apenas "@AGENTS.md" (+ notas específicas, se houver)
├── README.md                      # Para humanos: o que é, como usar o template, como adaptar
├── Makefile                       # Interface de comandos agnóstica de stack
├── harness.config.yaml            # Config do harness: ferramentas-alvo, paths protegidos, limites
│
├── .agents/                       # CANÔNICO e neutro de ferramenta
│   ├── skills/                    # Agent Skills (padrão aberto SKILL.md)
│   │   ├── create-plan/SKILL.md
│   │   ├── execute-plan/SKILL.md
│   │   ├── write-adr/SKILL.md
│   │   ├── code-review/SKILL.md
│   │   ├── debug-failing-check/SKILL.md
│   │   └── harness-retro/SKILL.md # transforma erro do agente em regra/teste/hook
│   ├── agents/                    # Papéis de subagentes (markdown + frontmatter neutro)
│   │   ├── planner.md
│   │   ├── implementer.md
│   │   ├── reviewer.md
│   │   └── security-reviewer.md
│   ├── commands/                  # Prompts reutilizáveis (viram slash commands nos adapters)
│   │   ├── plan.md
│   │   ├── implement.md
│   │   ├── review.md
│   │   └── handoff.md
│   └── mcp/servers.yaml           # Servidores MCP declarados de forma neutra
│
├── .claude/                       # GERADO (adapter Claude Code) — settings, hooks, skills, agents, commands
├── .github/
│   ├── copilot-instructions.md    # GERADO (adapter Copilot)
│   ├── workflows/ci.yml           # make check + harness-lint
│   ├── workflows/harness-gc.yml   # job agendado de garbage collection
│   └── pull_request_template.md
├── (outros adapters gerados conforme harness.config.yaml: .cursor/rules, GEMINI.md, .codex/…)
│
├── scripts/
│   ├── harness/
│   │   ├── sync.(sh|py)           # gera adapters a partir de .agents/ + AGENTS.md
│   │   ├── lint.(sh|py)           # valida o harness (ver Fase 6)
│   │   ├── gc.(sh|py)             # garbage collection (planos velhos, links, tamanho)
│   │   └── init.(sh|py)           # inicializa projeto novo a partir do template
│   └── hooks/                     # lógica de hooks em shell puro, chamada por qualquer adapter
│       ├── protect-paths.sh       # bloqueia escrita em paths protegidos
│       ├── format-changed.sh      # formata arquivos alterados
│       ├── check-on-stop.sh       # roda checks rápidos ao fim da tarefa
│       └── scan-secrets.sh        # gitleaks ou equivalente
│
├── docs/
│   ├── architecture/
│   │   ├── overview.md            # visão C4 nível 1–2 (placeholder)
│   │   └── boundaries.md          # camadas e regras de dependência
│   ├── adr/0000-template.md       # Architecture Decision Records
│   ├── adr/0001-adopt-agents-md-as-source-of-truth.md
│   ├── plans/
│   │   ├── TEMPLATE.md            # formato de exec plan
│   │   ├── active/
│   │   └── completed/
│   ├── specs/TEMPLATE.md          # especificação de feature (o quê/por quê)
│   ├── conventions/               # estilo, testes, git, segurança
│   ├── harness/
│   │   ├── how-it-works.md        # explica o harness (ótimo para portfólio)
│   │   ├── adapters.md            # matriz ferramenta × recurso suportado
│   │   └── learnings.md           # log do ratchet: erro → contramedida
│   └── glossary.md
│
├── ai/                            # OPCIONAL: módulo para apps que usam LLM em runtime
│   ├── README.md
│   ├── prompts/                   # prompts versionados (arquivos, não strings no código)
│   ├── evals/                     # datasets + critérios de avaliação
│   └── providers.md               # contrato de porta/adapter para provedores de LLM
│
├── examples/                      # exemplos mínimos por stack (java, python, node, go)
│   └── README.md
├── .pre-commit-config.yaml
├── .editorconfig
├── .gitignore
└── LICENSE
```

---

## 3. Fases

### Fase 1 — Fundação do repositório
- Criar `README.md`, `LICENSE` (MIT), `.gitignore`, `.editorconfig`, `CONTRIBUTING.md`.
- Criar `Makefile` com targets padronizados que **falham com mensagem clara** quando não implementados:
  `setup`, `fmt`, `lint`, `typecheck`, `test`, `test-fast`, `build`, `check` (= fmt-check + lint + typecheck + test), `harness-sync`, `harness-lint`, `harness-gc`.
- Criar `harness.config.yaml` com: `targets` (ex.: `[claude, copilot, cursor, codex, gemini]`), `protected_paths` (ex.: `.github/workflows/**`, `harness.config.yaml`, `**/*.lock`, `.env*`), `limits` (ex.: `agents_md_max_lines: 150`, `skill_max_lines: 300`), `plans.stale_after_days`.

**Aceite:** `make help` lista todos os targets; `make check` roda e falha de forma explícita com "not implemented for this stack".

### Fase 2 — Contrato do agente (`AGENTS.md`)
Escrever `AGENTS.md` **curto** (alvo < 150 linhas), funcionando como mapa:
1. Propósito do projeto (placeholder) e onde está a arquitetura.
2. **Comandos** (`make …`) e quando rodar cada um (`test-fast` entre edições, `check` antes de concluir).
3. Fluxo de trabalho: *explore → plan → implement → verify → handoff*; tarefas não triviais exigem plano em `docs/plans/active/`.
4. Regras de arquitetura e limites (link para `docs/architecture/boundaries.md`).
5. Invariantes de segurança (sem segredos, sem desativar testes, não editar `protected_paths` — pedir ao humano).
6. Definition of Done.
7. Índice de `docs/` e `.agents/skills/` com uma linha cada (progressive disclosure).

Criar `CLAUDE.md` contendo `@AGENTS.md` e nada mais além de notas estritamente específicas do Claude.

**Aceite:** `AGENTS.md` abaixo do limite configurado; todos os links relativos resolvem.

### Fase 3 — Conhecimento versionado (`docs/`)
- Templates: `adr/0000-template.md` (formato Nygard/MADR), `plans/TEMPLATE.md`, `specs/TEMPLATE.md`.
- `plans/TEMPLATE.md` deve conter: contexto, objetivo, fora de escopo, passos com checkbox, critérios de aceite verificáveis por comando, riscos, log de decisões, **seção de handoff** (estado atual, próximo passo, arquivos tocados) para retomar em sessão nova.
- ADR-0001: adoção de AGENTS.md + `.agents/` como fonte única e adapters gerados.
- `docs/harness/how-it-works.md`: diagrama (Mermaid) do fluxo contexto → ferramentas → verificação → ratchet.
- `docs/conventions/`: `testing.md`, `git.md` (Conventional Commits, PR pequeno), `security.md`, `code-style.md` (só o que difere dos defaults da linguagem).

**Aceite:** templates preenchíveis; diagrama renderiza no GitHub.

### Fase 4 — Skills, subagentes e comandos canônicos (`.agents/`)
- Cada skill segue o padrão aberto Agent Skills: pasta com `SKILL.md` (frontmatter `name`, `description`) + arquivos de apoio opcionais. `description` deve dizer **quando** usar.
- Skills mínimas: `create-plan`, `execute-plan`, `write-adr`, `code-review`, `debug-failing-check`, `harness-retro`.
- Subagentes em `.agents/agents/*.md` com frontmatter neutro: `name`, `description`, `tools` (lista abstrata: `read`, `write`, `shell`, `web`), `model_hint` (`fast` | `balanced` | `deep`). O sync traduz para o formato de cada ferramenta (ignorando campos sem suporte).
  - `planner`: só leitura, produz plano.
  - `implementer`: executa um plano aprovado.
  - `reviewer`: revisa diff contra `docs/conventions` e o plano, sem editar.
  - `security-reviewer`: foco em OWASP/secrets/dependências.
- Comandos em `.agents/commands/*.md` (`plan`, `implement`, `review`, `handoff`).

**Aceite:** todo `SKILL.md` e agente tem frontmatter válido; `harness-lint` (Fase 6) valida.

### Fase 5 — Adapters e sincronização
- Implementar `scripts/harness/sync` (Python 3 sem dependências externas além de PyYAML, ou bash+yq — escolher um e justificar em ADR-0002).
- Para cada `target` em `harness.config.yaml`, gerar:
  - **Claude Code:** `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `.claude/settings.json` com hooks chamando `scripts/hooks/*` (PreToolUse → `protect-paths.sh`; PostToolUse → `format-changed.sh`; Stop → `check-on-stop.sh`) e permissões (deny para `.env*`, comandos destrutivos). MCP em `.mcp.json`.
  - **Copilot:** `.github/copilot-instructions.md` (derivado de `AGENTS.md`) e skills/agents no formato suportado.
  - **Cursor / Codex / Gemini CLI:** apenas o que cada um suporta (consultar docs; registrar matriz em `docs/harness/adapters.md`).
- Todo arquivo gerado começa com cabeçalho `GENERATED BY scripts/harness/sync — DO NOT EDIT`.
- `scripts/hooks/*.sh`: lógica em shell puro, recebendo paths por argumento; wrappers finos por ferramenta convertem o input (ex.: JSON via stdin no Claude) em argumentos. Assim a mesma lógica serve a Claude, git hooks e CI.

**Aceite:** `make harness-sync` é idempotente (rodar 2x não gera diff); remover um target do config e sincronizar não apaga nada sem confirmação (listar órfãos e pedir permissão).

### Fase 6 — Feedback loops e guardrails determinísticos
- `scripts/harness/lint`: valida
  - limites de tamanho (`AGENTS.md`, skills);
  - links relativos em `AGENTS.md` e `docs/`;
  - frontmatter de skills/agentes;
  - adapters em sincronia (`sync --check` sem diff);
  - nenhum plano em `active/` sem checklist.
- `.pre-commit-config.yaml`: formatação genérica, `scan-secrets`, `harness-lint`.
- `.github/workflows/ci.yml`: `make check` + `make harness-lint`. Paths protegidos exigem CODEOWNERS.
- `.github/pull_request_template.md`: link para plano, checklist de DoD, "o agente gerou este código?".

**Aceite:** CI verde no template; um commit com segredo falso é bloqueado; editar arquivo gerado à mão falha no `harness-lint`.

### Fase 7 — Garbage collection e ratchet
- `scripts/harness/gc`: relata planos em `active/` além de `stale_after_days`, docs não referenciados, TODOs antigos. **Só relata**, nunca apaga.
- `.github/workflows/harness-gc.yml`: agendado semanal, abre issue com o relatório.
- `docs/harness/learnings.md`: tabela `data | erro do agente | causa | contramedida (regra/teste/hook/doc) | link`.
- Skill `harness-retro`: guia o agente a propor a contramedida mais determinística possível (preferência: teste/lint > hook > texto em AGENTS.md).

**Aceite:** `make harness-gc` gera relatório legível; workflow válido.

### Fase 8 — (Opcional) Módulo de IA em runtime (`ai/`)
Para projetos cuja aplicação chama LLMs:
- `providers.md`: contrato de porta (hexagonal) — `complete`, `stream`, `embed`, `tool_call` — com adapters por provedor; nenhuma lib de provedor fora da camada de adapter.
- `prompts/`: um arquivo por prompt, com frontmatter (`id`, `version`, `model_hint`, `inputs`), carregado por chave.
- `evals/`: formato de dataset (JSONL: input, expected/rubric) + target `make eval`; regressão de eval quebra CI quando habilitado.
- Notas de observabilidade (trace por chamada, custo, latência) e guardrails (validação de saída com schema, limites de tokens, PII).

**Aceite:** documentação e estrutura prontas, sem dependência de SDK específico.

### Fase 9 — Bootstrap de novo projeto e publicação
- `scripts/harness/init`: pergunta nome, descrição, stack e targets; substitui placeholders; opcionalmente remove `examples/` e `ai/` **somente após confirmação**.
- `examples/`: README explicando como implementar os targets do `Makefile` em Java (Maven/Gradle), Python (uv), Node (pnpm) e Go.
- README final: badge de CI, diagrama, "Use this template", passo a passo de adoção, matriz de ferramentas suportadas, seção "Why harness engineering" com referências.
- Marcar o repositório como *Template repository* no GitHub (passo manual, documentar no README).

**Aceite:** clonar o template, rodar `init` e `make harness-sync` produz um projeto funcional com CI verde.

---

## 4. Definition of Done global
- [ ] `make check` e `make harness-lint` verdes.
- [ ] `make harness-sync` idempotente.
- [ ] Nenhum arquivo gerado editado manualmente.
- [ ] `AGENTS.md` dentro do limite e com todos os links válidos.
- [ ] ADRs registradas para decisões não óbvias.
- [ ] Plano movido de `docs/plans/active/` para `completed/` com handoff final.

## 5. Fora de escopo (v1)
- Código de aplicação real (apenas exemplos mínimos).
- Orquestração multiagente em runtime (frameworks tipo LangGraph etc.).
- Adapters para ferramentas sem suporte a instruções em arquivo.

## 6. Referências
- AGENTS.md (padrão aberto): https://agents.md
- Agent Skills (padrão aberto SKILL.md): https://agentskills.io
- Awesome Harness Engineering (curadoria: Thoughtworks, Anthropic, OpenAI, HumanLayer, LangChain): https://github.com/walkinglabs/awesome-harness-engineering
- The Emerging "Harness Engineering" Playbook: https://www.ignorance.ai/p/the-emerging-harness-engineering
- Anthropic — Claude Code best practices: https://www.anthropic.com/engineering/claude-code-best-practices
- Anthropic — Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
