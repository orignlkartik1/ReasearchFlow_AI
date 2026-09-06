# Architecture

ResearchFlow AI is organized around a FastAPI backend, a Telegram application managed by that backend, and a Google ADK agent graph.

For fuller design detail, use [HLD.md](./HLD.md) for the system-level view and [LLD.md](./LLD.md) for module-level behavior.

## Runtime View

```text
API client or Telegram
        |
        v
my_agent.backend.main
        |
        +-- /chat
        +-- /telegram/webhook
        |
        v
my_agent.backend.adk_runner
        |
        v
my_agent.agent:root_agent
        |
        +-- academic_websearch_agent
        |       |
        |       v
        |   ADK google_search tool
        |
        +-- academic_newresearch_agent
```

## Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| FastAPI app | `my_agent/backend/main.py` | Exposes `/chat` and `/telegram/webhook`, validates webhook secrets, manages Telegram app lifecycle |
| ADK runner | `my_agent/backend/adk_runner.py` | Creates in-memory sessions, runs the root agent, extracts final response text |
| Telegram bot | `my_agent/backend/telegram.py` | Handles `/start`, text messages, webhook updates, webhook setup, and optional debug polling |
| Telegram messages | `my_agent/backend/telegram_messages.py` | Splits long responses and handles Telegram send/edit/delete failures |
| Coordinator agent | `my_agent/agent.py` | Defines the root ADK agent and wires sub-agents as tools |
| Environment loader | `my_agent/env.py` | Loads `my_agent/.env` and validates required values |
| Web research sub-agent | `my_agent/sub_agents/academic_webresearch` | Searches for recent citing or related papers using ADK Google Search |
| Future research sub-agent | `my_agent/sub_agents/academic_newresearch` | Synthesizes research gaps and future directions |

## Data Flow

1. The user sends a request through `/chat` or Telegram.
2. FastAPI validates the request body or Telegram webhook secret.
3. `adk_runner.ask_agent` creates or reuses an in-memory session for `user_id`.
4. The coordinator agent processes the request.
5. The coordinator invokes sub-agents through ADK `AgentTool`.
6. The final ADK response is returned as JSON or sent back through Telegram.

## Session Model

Sessions are stored in `InMemorySessionService`. The current `session_id` is the same as `user_id`, which gives each user one active conversation context per backend process.

This is simple and useful for local development, but it has deployment limits:

- Sessions are lost on restart.
- Multiple backend replicas do not share session state.
- There is no retention policy or user-level history management.

Persistent session storage should be introduced before multi-instance production deployment.

## Telegram Modes

Webhook mode is the intended runtime mode. `main.py` initializes the Telegram app during FastAPI lifespan and optionally registers a webhook when `TELEGRAM_WEBHOOK_URL` is configured.

Webhook requests can be protected with `TELEGRAM_WEBHOOK_SECRET`. When configured, FastAPI validates Telegram's `X-Telegram-Bot-Api-Secret-Token` header before accepting updates.

Polling mode is guarded by `ENABLE_TELEGRAM_POLLING=1` and should be used only for local debugging.
