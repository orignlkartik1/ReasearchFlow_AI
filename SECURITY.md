# Security Policy

## Supported Version

The project is currently pre-1.0. Security fixes should target the main development branch unless a release branch is created.

## Secrets

Never commit real credentials. The following values are sensitive:

- `GOOGLE_API_KEY`
- `TELEGRAM_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- Provider keys such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GROQ_API_KEY`

Use `my_agent/.env` for local development and a secret manager or deployment environment variables in production.

## Webhook Security

For deployed Telegram webhooks:

- Set `TELEGRAM_WEBHOOK_SECRET`.
- Serve FastAPI over HTTPS.
- Do not expose stack traces publicly.
- Restrict logs so they do not include tokens or full request headers.

## Input Handling

User messages are untrusted input. Agent responses should not be treated as verified facts without source review. Future API-facing deployments should add:

- Request size limits.
- Rate limiting.
- Authentication.
- Abuse monitoring.
- Persistent audit logs with secret redaction.

## Dependency Security

- Keep `uv.lock` committed.
- Review dependency updates before merging.
- Regenerate the lock file after dependency changes.
- Run vulnerability scanning before production deployment when available.

## Reporting Issues

Report security issues privately to the project maintainer. Include:

- Affected files or endpoints.
- Reproduction steps.
- Impact assessment.
- Suggested mitigation if known.

Do not publish exploitable details until a fix is available.

