# Low-Level Design

## ResearchFlow AI

## 1. Purpose

This Low-Level Design (LLD) describes the concrete modules, functions, data contracts, and runtime logic used by the current ResearchFlow AI implementation. It should be read with [HLD.md](./HLD.md), [ARCHITECTURE.md](./ARCHITECTURE.md), and [SRS.md](./SRS.md).

## 2. Module Design

| Module | Primary Items | Responsibility |
|--------|---------------|----------------|
| `my_agent/env.py` | `load_environment`, `require_env` | Loads `my_agent/.env` and validates required values |
| `my_agent/llm_config.py` | model getters, validators, retry detection | Handles model selection, fallback lists, credential checks |
| `my_agent/agent.py` | `create_root_agent`, `root_agent` | Builds the coordinator agent and wires sub-agent tools |
| `my_agent/prompt.py` | `ACADEMIC_COORDINATOR_PROMPT` | Defines coordinator behavior |
| `my_agent/backend/main.py` | `app`, `/chat`, `/telegram/webhook` | Defines FastAPI app, routes, Telegram lifecycle |
| `my_agent/backend/adk_runner.py` | `ask_agent`, `_run_once`, `_model_attempts` | Runs ADK agents with in-memory sessions and fallback attempts |
| `my_agent/backend/telegram.py` | `start`, `chat`, webhook helpers | Handles Telegram user interactions |
| `my_agent/backend/telegram_messages.py` | split/send/edit/delete helpers | Handles Telegram message size and API edge cases |
| `academic_webresearch/agent.py` | `create_academic_websearch_agent` | Creates retrieval sub-agent |
| `academic_newresearch/agent.py` | `create_academic_newresearch_agent` | Creates synthesis sub-agent |

## 3. API Contracts

### 3.1 `POST /chat`

Request model:

```python
class ChatRequest(BaseModel):
    user_id: str
    message: str
```

Success response:

```json
{
  "response": "agent response text"
}
```

Error behavior:

- Runtime agent failures are converted to `503`.
- FastAPI/Pydantic validation handles invalid request bodies.

### 3.2 `POST /telegram/webhook`

Inputs:

- Telegram update JSON body.
- Optional `X-Telegram-Bot-Api-Secret-Token` header.

Behavior:

- Rejects invalid webhook secrets with `403`.
- Rejects invalid JSON with `400`.
- Schedules Telegram update processing in a background task.
- Returns `{"ok": true}` after accepting the update.

## 4. Agent Construction

`create_root_agent` accepts optional `llm_model` and `search_model` values. When values are not provided, they are loaded from environment configuration.

```text
create_root_agent
    |
    +-- create_academic_websearch_agent(search_model)
    |
    +-- create_academic_newresearch_agent(llm_model)
```

The coordinator exposes both sub-agents as ADK `AgentTool` instances.

## 5. Session Handling

`adk_runner.py` uses:

- `APP_NAME = "ResearchFlowAI"`
- `InMemorySessionService`
- `_created_sessions` set

Session logic:

```text
ask_agent(user_id, message)
    |
    +-- validate_model_environment()
    +-- session_id = user_id
    +-- _ensure_session(user_id, session_id)
    +-- build available model attempts
    +-- run until success or non-retryable failure
```

Current limitation: `_created_sessions` is process-local and does not persist across restarts.

## 6. Model Fallback Logic

Environment variables:

- `LLM_MODEL`
- `LLM_MODEL_FALLBACKS`
- `SEARCH_MODEL`
- `SEARCH_MODEL_FALLBACKS`

Flow:

1. Load ordered primary and fallback models.
2. Validate model support through ADK `LLMRegistry`.
3. Validate that search models are Gemini-compatible.
4. Filter models with missing provider credentials.
5. Build `(llm_model, search_model)` attempts.
6. Retry only when `is_retryable_llm_error` detects transient provider failure markers.

Non-retryable errors are returned immediately as runtime failures.

## 7. Telegram Message Handling

Telegram response handling is split across `telegram.py` and `telegram_messages.py`.

Important constants:

- `TELEGRAM_MESSAGE_LIMIT = 4000`
- `ATTACHMENT_THRESHOLD = 100000000`

Long response behavior:

1. If response fits, send one message.
2. If response exceeds the message limit, split by paragraph, newline, then space.
3. If response exceeds the attachment threshold, create a temporary text file and send it as a document.
4. Log Telegram API failures without crashing the process.

## 8. Environment Loading

`my_agent/env.py` loads:

```text
my_agent/.env
```

`require_env(name)` raises `RuntimeError` when a required variable is missing. The Telegram bot uses this for `TELEGRAM_TOKEN`.

The FastAPI app calls `load_environment()` before reading webhook configuration so local `.env` webhook settings are available at startup.

## 9. Error Handling

| Area | Error | Handling |
|------|-------|----------|
| Missing required env | `RuntimeError` | Startup or request failure with actionable message |
| Invalid webhook secret | `HTTPException(403)` | Request rejected |
| Invalid webhook JSON | `HTTPException(400)` | Request rejected |
| Agent non-retryable failure | `RuntimeError` then `HTTPException(503)` | Returned to API caller |
| Telegram send/edit/delete failure | Logged exception | Bot continues processing |
| Transient provider failure | Retry next configured attempt | Fails only after all attempts fail |

## 10. Extension Points

- Add new sub-agents under `my_agent/sub_agents/` and wire them into `create_root_agent`.
- Add persistent session storage by replacing `InMemorySessionService`.
- Add direct PDF parsing before coordinator invocation.
- Add authentication and rate limiting at the FastAPI layer.
- Add structured logging and metrics around `ask_agent`.

