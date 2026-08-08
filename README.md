# ResearchFlow AI

ResearchFlow AI is a multi-agent academic research assistant built with Google ADK, FastAPI, and a Telegram bot interface. It helps researchers analyze seminal papers, find recent citing work, and synthesize practical future research directions.

For detailed requirements, see [SRS.md](./SRS.md). For architecture details, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Features

- Coordinator agent that manages the full research workflow.
- Web research sub-agent that uses Google Search through ADK.
- Future research sub-agent that synthesizes research gaps and promising directions.
- FastAPI `/chat` endpoint for direct API use.
- Telegram bot support through webhook mode, with optional local polling for debugging.
- In-memory ADK session management for multi-turn conversations.
- Configurable LLM and search models with fallback support.
- Long Telegram response handling with message splitting and file attachment fallback.

## Project Structure

```text
ResearchFlow_AI/
+-- my_agent/
|   +-- __init__.py
|   +-- agent.py
|   +-- prompt.py
|   +-- env.py
|   +-- llm_config.py
|   +-- .env.example
|   +-- backend/
|   |   +-- main.py
|   |   +-- adk_runner.py
|   |   +-- telegram.py
|   |   +-- telegram_messages.py
|   +-- sub_agents/
|       +-- academic_webresearch/
|       +-- academic_newresearch/
+-- README.md
+-- SRS.md
+-- ARCHITECTURE.md
+-- DESIGN.md
+-- SECURITY.md
+-- CONTRIBUTING.md
+-- CODE_OF_CONDUCT.md
+-- CHANGELOG.md
+-- pyproject.toml
+-- uv.lock
```

## Requirements

- Python `>=3.13`
- `uv` package manager
- Google API key for Google ADK and Gemini
- Telegram bot token for Telegram integration

Primary dependencies are declared in [pyproject.toml](./pyproject.toml):

- `google-adk==2.3.0`
- `fastapi>=0.139.0`
- `uvicorn>=0.51.0`
- `python-telegram-bot>=22.8`
- `httpx>=0.28.1`
- `python-dotenv>=1.2.2`

## Setup

Install dependencies:

```bash
uv sync
```

Create `my_agent/.env` from `my_agent/.env.example` and configure the required values:

```text
GOOGLE_API_KEY=your_google_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
```

Optional backend and webhook settings:

```text
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
TELEGRAM_WEBHOOK_URL=https://your-domain.example/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret
ENABLE_TELEGRAM_POLLING=0
```

Optional model settings:

```text
LLM_MODEL=gemini-2.5-flash
LLM_MODEL_FALLBACKS=openai/gpt-4.1,anthropic/claude-sonnet-4-5
SEARCH_MODEL=gemini-2.5-flash
SEARCH_MODEL_FALLBACKS=gemini-2.5-flash-lite
```

Only configure provider credentials for models you actually use.

## Running

Start the FastAPI app:

```bash
python -m uvicorn my_agent.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Test the API:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","message":"Analyze Attention is All You Need and find recent citing papers."}'
```

Use Telegram webhooks by setting `TELEGRAM_WEBHOOK_URL` and running the FastAPI app. For temporary local debugging only, polling can be enabled:

```bash
set ENABLE_TELEGRAM_POLLING=1
python -m my_agent.backend.telegram
```

## API

### POST `/chat`

Request:

```json
{
  "user_id": "unique-user-id",
  "message": "Analyze a seminal paper and identify future research directions."
}
```

Response:

```json
{
  "response": "Agent response text"
}
```

### POST `/telegram/webhook`

Receives Telegram updates. If `TELEGRAM_WEBHOOK_SECRET` is set, the endpoint validates the `X-Telegram-Bot-Api-Secret-Token` header.

## Workflow

1. A user sends a paper title, metadata, or research request.
2. The coordinator agent builds paper context.
3. The web research sub-agent searches for recent citing papers.
4. The future research sub-agent synthesizes research gaps and directions.
5. The coordinator returns a structured response to the API or Telegram user.
6. The in-memory ADK session preserves context for follow-up questions.

## Documentation

- [SRS.md](./SRS.md): software requirements specification
- [ARCHITECTURE.md](./ARCHITECTURE.md): runtime structure and data flow
- [DESIGN.md](./DESIGN.md): product, API, and agent design decisions
- [SECURITY.md](./SECURITY.md): security policy and operational guidance
- [CONTRIBUTING.md](./CONTRIBUTING.md): contribution workflow
- [CHANGELOG.md](./CHANGELOG.md): project history
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md): community standards

## Current Limitations

- Sessions are stored in memory and are lost on process restart.
- Search quality depends on Google Search result availability.
- PDF ingestion is specified as a target capability, but the current code accepts text queries and paper metadata rather than parsing uploaded PDFs directly.
- Telegram polling is intentionally disabled by default in favor of webhook mode.

## License

This project currently references the MIT License. Add a `LICENSE` file before distributing the project publicly.
