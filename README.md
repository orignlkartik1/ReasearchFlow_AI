# ResearchFlow AI

ResearchFlow AI is a multi-agent academic research assistant built with Google ADK, FastAPI, and a Telegram bot interface. It helps users analyze seminal papers or research prompts, search for recent citing work, and synthesize future research directions.

Detailed requirements and design notes are maintained in [SRS.md](./SRS.md), [DESIGN.md](./DESIGN.md), [HLD.md](./HLD.md), and [LLD.md](./LLD.md).

## Current Capabilities

1. Accept research requests through `POST /chat`.
2. Accept Telegram updates through `POST /telegram/webhook`.
3. Run a Google ADK coordinator agent with two specialist sub-agents.
4. Search the web for recent academic work using the ADK Google Search tool.
5. Generate future research directions from the seminal paper context and recent papers.
6. Preserve per-user conversation context in memory while the backend process is running.
7. Split long Telegram responses and send extremely large responses as text attachments.

## Project Structure

```text
ResearchFlow_AI/
+-- my_agent/
|   +-- __init__.py
|   +-- agent.py                          # Root academic coordinator agent
|   +-- prompt.py                         # Coordinator prompt
|   +-- env.py                            # .env loading and required env checks
|   +-- backend/
|   |   +-- __init__.py
|   |   +-- main.py                       # FastAPI app, /chat, Telegram webhook
|   |   +-- adk_runner.py                 # ADK Runner and in-memory sessions
|   |   +-- telegram.py                   # Telegram handlers and webhook helpers
|   |   +-- telegram_messages.py          # Long-message split/send helpers
|   +-- sub_agents/
|       +-- academic_webresearch/
|       |   +-- agent.py                  # Google Search-backed retrieval agent
|       |   +-- prompt.py                 # Retrieval prompt
|       +-- academic_newresearch/
|           +-- agent.py                  # Future research synthesis agent
|           +-- prompt.py                 # Synthesis prompt
+-- README.md
+-- SRS.md
+-- DESIGN.md
+-- HLD.md
+-- LLD.md
+-- ARCHITECTURE.md
+-- pyproject.toml
+-- uv.lock
```

## Architecture Summary

```text
Telegram user or API client
        |
        v
FastAPI app: my_agent.backend.main
        |
        +-- /chat
        +-- /telegram/webhook
        |
        v
ADK runner: my_agent.backend.adk_runner
        |
        v
Coordinator agent: my_agent.agent
        |
        +-- academic_websearch_agent + google_search
        +-- academic_newresearch_agent
```

The FastAPI app initializes and starts the Telegram application during its lifespan. When `TELEGRAM_WEBHOOK_URL` is configured, startup also registers the Telegram webhook. Telegram message handling calls the ADK runner directly; it does not require a separate bot polling process in normal deployment.

## Main Components

### Coordinator Agent

`my_agent/agent.py` exports `root_agent`, a Google ADK `Agent` named `academic_coordinator` using `gemini-2.5-flash`.

The coordinator owns the user-facing workflow and exposes two sub-agents through `AgentTool`:

- `academic_websearch_agent` for recent citing-paper discovery.
- `academic_newresearch_agent` for future research direction synthesis.

### Web Research Sub-Agent

`my_agent/sub_agents/academic_webresearch/agent.py` defines an agent that uses ADK's `google_search` tool. Its prompt asks it to identify papers from the current year and previous year that cite or extend the seminal work, group them by year, and include links where available.

### New Research Sub-Agent

`my_agent/sub_agents/academic_newresearch/agent.py` defines an agent that synthesizes at least 10 future research areas when enough paper context is available. It focuses on novelty, practical utility, unexpected directions, and emerging interest.

### FastAPI Backend

`my_agent/backend/main.py` exposes:

- `POST /chat` for direct API usage.
- `POST /telegram/webhook` for Telegram updates.

The app validates Telegram webhook secrets when `TELEGRAM_WEBHOOK_SECRET` is set, schedules Telegram update processing as a background task, and manages the Telegram application's startup and shutdown lifecycle.

### ADK Runner

`my_agent/backend/adk_runner.py` owns agent execution:

- Uses `Runner` from Google ADK.
- Uses `InMemorySessionService` for process-local conversation state.
- Creates one session per `user_id`.
- Extracts final text from ADK final response events.
- Converts execution failures into `RuntimeError` for callers.

### Telegram Integration

`my_agent/backend/telegram.py` uses `python-telegram-bot`.

- `/start` sends a short welcome message.
- Text messages show typing status and a processing message.
- User messages are sent to `ask_agent(user_id, message)`.
- Long responses are sent through `telegram_messages.py`.
- Long polling is disabled by default and only runs when `ENABLE_TELEGRAM_POLLING=1`.

## Requirements

The project uses `uv` and declares dependencies in `pyproject.toml`.

Current requirements include:

- Python `>=3.13`
- `fastapi`
- `google-adk==2.3.0`
- `pydantic`
- `python-dotenv`
- `python-telegram-bot`
- `uvicorn`

`pyproject.toml` also currently lists `aiogram` and `httpx`, but the active Telegram implementation uses `python-telegram-bot` and does not call the backend through HTTP.

## Setup

Install dependencies:

```bash
uv sync
```

Create `my_agent/.env` or provide equivalent process environment variables:

```text
GOOGLE_API_KEY=your_google_api_key
TELEGRAM_TOKEN=your_telegram_bot_token

# Optional: production webhook registration and verification
TELEGRAM_WEBHOOK_URL=https://your-domain.example/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=your_random_secret

# Optional: local debugging only
ENABLE_TELEGRAM_POLLING=1
```

## Running

### FastAPI Backend

```bash
python -m uvicorn my_agent.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Test `/chat`:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","message":"Analyze Attention Is All You Need and find recent citing papers."}'
```

Expected response shape:

```json
{
  "response": "Agent response text"
}
```

### Telegram Webhook Mode

Run the FastAPI app with `TELEGRAM_TOKEN` configured. If `TELEGRAM_WEBHOOK_URL` is set, startup registers the webhook automatically:

```bash
python -m uvicorn my_agent.backend.main:app --host 0.0.0.0 --port 8000
```

Telegram will send updates to:

```text
POST /telegram/webhook
```

When `TELEGRAM_WEBHOOK_SECRET` is configured, Telegram requests must include the matching `X-Telegram-Bot-Api-Secret-Token` header.

### Local Telegram Polling

Polling is intended only for temporary local debugging:

```bash
$env:ENABLE_TELEGRAM_POLLING="1"
python -m my_agent.backend.telegram
```

Without `ENABLE_TELEGRAM_POLLING=1`, the module raises an error telling you to use the FastAPI webhook path.

## API

### `POST /chat`

Request:

```json
{
  "user_id": "unique_user_identifier",
  "message": "research question, paper title, citation, abstract, or follow-up"
}
```

Success:

```json
{
  "response": "agent response text"
}
```

Agent execution failures return `503` with a `detail` field.

### `POST /telegram/webhook`

Accepts a Telegram update JSON payload and returns:

```json
{
  "ok": true
}
```

Invalid JSON returns `400`. Invalid webhook secrets return `403` when webhook secret validation is enabled.

## Development Notes

- Agent behavior is controlled primarily through prompt files.
- The coordinator and both sub-agents currently use `gemini-2.5-flash`.
- Session state is process-local and is lost on restart.
- There is no persistent database yet.
- Direct PDF ingestion is part of the intended product direction but is not implemented in the current code.
- Web research quality depends on Google Search results returned through the ADK tool.

## Documentation

- [SRS.md](./SRS.md): requirements, constraints, acceptance criteria, and revision history.
- [DESIGN.md](./DESIGN.md): product, interaction, response, API, and configuration design.
- [HLD.md](./HLD.md): system context, layers, data flow, deployment, and security view.
- [LLD.md](./LLD.md): module-level functions, contracts, runtime behavior, and extension points.
- [ARCHITECTURE.md](./ARCHITECTURE.md): concise architecture reference.

## Future Enhancements

- Persistent sessions with Redis, PostgreSQL, or another shared store.
- Direct PDF upload and parsing.
- Scholarly database integrations.
- Citation graph visualization.
- Structured exports such as Markdown, JSON, BibTeX, or PDF.
- Authentication and rate limiting for public deployments.
- Tests for API, Telegram message splitting, webhook validation, and agent runner behavior.

## License

This project is licensed under the MIT License. See the license file for details.
