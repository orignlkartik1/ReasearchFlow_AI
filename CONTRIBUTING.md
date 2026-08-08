# Contributing

Thanks for improving ResearchFlow AI. This project is still early, so contributions should keep changes focused, documented, and easy to verify.

## Development Setup

1. Install Python `>=3.13`.
2. Install `uv`.
3. Run:

```bash
uv sync
```

4. Copy `my_agent/.env.example` to `my_agent/.env` and set local credentials.

Do not commit real `.env` files, API keys, bot tokens, or generated caches.

## Workflow

1. Create a feature branch.
2. Keep changes scoped to one concern.
3. Update documentation when behavior, configuration, APIs, or requirements change.
4. Run syntax checks and relevant tests before opening a pull request.
5. Describe what changed, why it changed, and how it was verified.

## Code Guidelines

- Keep backend routes thin and delegate agent execution to service modules.
- Keep prompts in `prompt.py` files.
- Prefer async I/O in Telegram and FastAPI code.
- Keep user-facing errors actionable but avoid leaking secrets.
- Add comments only for non-obvious logic.
- Preserve existing module boundaries unless there is a clear reason to change them.

## Documentation Guidelines

Update the relevant document when changing project behavior:

- `README.md` for setup, running, and user-facing behavior.
- `SRS.md` for requirements.
- `ARCHITECTURE.md` for component or data-flow changes.
- `DESIGN.md` for workflow, API, or UX decisions.
- `SECURITY.md` for credential, deployment, or risk changes.
- `CHANGELOG.md` for notable changes.

## Pull Request Checklist

- [ ] Code compiles.
- [ ] Relevant tests or manual verification were run.
- [ ] Documentation is updated.
- [ ] No secrets are committed.
- [ ] New configuration values are documented.
- [ ] Error behavior is handled intentionally.

