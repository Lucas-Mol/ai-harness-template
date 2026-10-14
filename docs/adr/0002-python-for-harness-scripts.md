# ADR-0002: Use Python 3 + PyYAML for harness scripts

- **Status:** Accepted
- **Date:** 2026-10-14
- **Deciders:** template maintainers

## Context

The harness needs scripts to sync adapters, lint the harness, report garbage and bootstrap projects.
They parse YAML (config, frontmatter), emit JSON/TOML/Markdown and must run on Linux, macOS, Windows (WSL/Git Bash) and CI.

## Decision drivers

- Available almost everywhere, including CI runners, without a build step.
- Robust YAML parsing (frontmatter is YAML).
- Readable by contributors from any stack.

## Considered options

1. Bash + `yq` + `jq`.
2. Python 3 standard library + PyYAML.
3. A compiled CLI (Go/Rust).

## Decision

Python 3.10+ with PyYAML as the only third-party dependency (pinned in `scripts/harness/requirements.txt`).
Bash + yq was rejected because `yq` has two incompatible implementations and generating structured JSON/TOML in Bash is fragile.
A compiled CLI adds a build/release step to a template.

Hook *logic* stays in plain shell (`scripts/hooks/*.sh`) so git hooks and CI can call it without Python;
only the thin tool wrappers (e.g. Claude's JSON-on-stdin) use Python.

## Consequences

- **Positive:** one dependency, readable code, easy JSON/TOML generation.
- **Negative:** contributors need Python 3.10+ (`make harness-deps` installs PyYAML).
