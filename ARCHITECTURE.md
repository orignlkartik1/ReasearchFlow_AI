# Architecture

ResearchFlow AI is organized around a small FastAPI backend and a Google ADK agent graph.

For fuller design detail, use [HLD.md](./HLD.md) for the system-level view and [LLD.md](./LLD.md) for module-level behavior.

## Runtime View

```text
API client or Telegram
        |
        v
my_agent.backend.main
        |
        v
my_agent.backend.adk_runner
        |
        v
my_agent.agent:create_root_agent
        |
        +--> academic_websearch_agent
        |       |
        |       v
        |   ADK google_search tool
        |
        +--> academic_newresearch_agent
```

## Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| FastAPI app | `my_agent/backend/main.py` | Exposes `/chat` and `/telegram/webhook`, manages Telegram app lifecycle |
| ADK runner | `my_agent/backend/adk_runner.py` | Creates sessions, runs agents, applies fallback attempts |
| Telegram bot | `my_agent/backend/telegram.py` | Handles `/start`, text messages, webhook updates, and optional polling |
| Telegram messages | `my_agent/backend/telegram_messages.py` | Splits long responses and handles Telegram send/edit/delete failures |
| Coordinator agent | `my_agent/agent.py` | Creates the root ADK agent and wires sub-agents as tools |
| LLM config | `my_agent/llm_config.py` | Reads model settings, validates models, checks credentials, detects retryable errors |
| Environment loader | `my_agent/env.py` | Loads `my_agent/.env` and requires configured values |
| Web research sub-agent | `my_agent/sub_agents/academic_webresearch` | Searches for recent citing or related papers |
| Future research sub-agent | `my_agent/sub_agents/academic_newresearch` | Synthesizes research gaps and future directions |

## Data Flow

1. The user sends a request through `/chat` or Telegram.
2. FastAPI validates the request body or Telegram webhook secret.
3. `adk_runner.ask_agent` creates or reuses an in-memory session for `user_id`.
4. Configured model names and credentials are validated.
5. The coordinator agent processes the request.
6. The coordinator invokes sub-agents through ADK `AgentTool`.
7. The final ADK response is returned as JSON or sent back through Telegram.

## Session Model

Sessions are stored in `InMemorySessionService`. The current `session_id` is the same as `user_id`, which gives each user one active conversation context per backend process.

This is simple and useful for local development, but it has deployment limits:

- Sessions are lost on restart.
- Multiple backend replicas do not share session state.
- There is no retention policy or user-level history management.

Persistent session storage should be introduced before multi-instance production deployment.

## Model Fallback

`llm_config.py` reads:

- `LLM_MODEL`
- `LLM_MODEL_FALLBACKS`
- `SEARCH_MODEL`
- `SEARCH_MODEL_FALLBACKS`

The runner attempts available `(llm_model, search_model)` combinations. It retries only errors that look transient, such as rate limits, quota exhaustion, overloads, timeouts, or service unavailability.

Search models must remain Gemini-compatible because ADK's built-in `google_search` tool requires Gemini search support.

## Telegram Modes

Webhook mode is the intended runtime mode. `main.py` initializes the Telegram app during FastAPI lifespan and optionally registers a webhook when `TELEGRAM_WEBHOOK_URL` is configured.

Polling mode is guarded by `ENABLE_TELEGRAM_POLLING=1` and should be used only for local debugging.
