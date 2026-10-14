# Security

## Secrets

- Never commit secrets. Configuration comes from environment variables; document them in `.env.example` (no values).
- `scripts/hooks/scan-secrets.sh` runs in pre-commit, on agent edits and in CI. A false positive can be
  allowed per line with the comment `harness:allow-secret` — explain why in the PR.
- Never print secrets, tokens or personal data in logs or debug output.
- Agents are denied read access to `secret_files` (see `harness.config.yaml`).

## Input and output

- Validate all external input at the boundary (HTTP, CLI, files, LLM output).
- Use parameterised queries; never build SQL/shell commands by string concatenation.
- Encode output for its context (HTML, SQL, shell, logs).
- Treat LLM output as untrusted input: validate it against a schema before acting on it.

## Dependencies

- New dependencies need approval. Prefer well-maintained, widely used libraries.
- Pin versions with lock files (lock files are protected paths: humans update them).
- Enable automated vulnerability alerts (Dependabot/Renovate) in the hosting platform.

## Review

Run the `security-reviewer` subagent on changes touching auth, input handling, crypto, file/network I/O or dependencies.
Reference: [OWASP Top 10](https://owasp.org/www-project-top-ten/).
