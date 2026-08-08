# High-Level Design

## ResearchFlow AI

## 1. Purpose

This High-Level Design (HLD) describes the major system components, their responsibilities, external integrations, and runtime flows for ResearchFlow AI. It complements [SRS.md](./SRS.md), which defines requirements, and [LLD.md](./LLD.md), which describes implementation-level design.

## 2. System Context

ResearchFlow AI accepts academic research requests through an HTTP API or Telegram. It uses a Google ADK coordinator agent and two specialized sub-agents to analyze a seminal paper, discover recent citing work, and generate future research directions.

```text
User / API Client / Telegram
        |
        v
ResearchFlow AI Backend
        |
        +--> Google ADK / Gemini
        +--> Google Search tool
        +--> Telegram Bot API
```

## 3. High-Level Architecture

```text
+-------------------------+
| User Interface Layer    |
| - Telegram bot          |
| - HTTP API clients      |
+-----------+-------------+
            |
            v
+-------------------------+
| API Layer               |
| - FastAPI app           |
| - /chat                 |
| - /telegram/webhook     |
+-----------+-------------+
            |
            v
+-------------------------+
| Orchestration Layer     |
| - ADK Runner            |
| - Session service       |
| - Model fallback logic  |
+-----------+-------------+
            |
            v
+-------------------------+
| Agent Layer             |
| - Coordinator agent     |
| - Web research agent    |
| - Future research agent |
+-----------+-------------+
            |
            v
+-------------------------+
| External Services       |
| - Google ADK / Gemini   |
| - Google Search         |
| - Telegram Bot API      |
+-------------------------+
```

## 4. Major Components

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| UI | Telegram bot | Receives user messages, sends responses, supports `/start` |
| UI | API client | Calls `/chat` directly for integration or testing |
| API | FastAPI app | Handles HTTP validation, webhook security, app lifecycle |
| Orchestration | ADK runner | Creates sessions, executes agents, returns final response text |
| Orchestration | Model fallback | Validates configured models and retries transient provider failures |
| Agent | Coordinator | Owns user-facing workflow and invokes sub-agents |
| Agent | Web research | Uses Google Search to find recent citing or related papers |
| Agent | Future research | Synthesizes gaps and future research suggestions |
| Config | Environment loader | Loads `my_agent/.env` and process environment variables |

## 5. Core Data Flow

1. The user submits a message through Telegram or `POST /chat`.
2. FastAPI validates the request and delegates to `ask_agent`.
3. The ADK runner creates or reuses an in-memory session for the user.
4. Model configuration is validated.
5. The coordinator agent analyzes the request and builds paper context.
6. The coordinator invokes the web research sub-agent through `AgentTool`.
7. The coordinator invokes the future research sub-agent through `AgentTool`.
8. The final response is returned to FastAPI.
9. FastAPI returns JSON or the Telegram bot sends the response to the user.

## 6. Deployment View

Current target deployment is a single Python process running FastAPI with Uvicorn.

```text
Uvicorn process
    |
    +-- FastAPI app
    +-- Telegram application lifecycle
    +-- In-memory ADK sessions
    +-- Agent execution
```

For production scaling, persistent sessions and shared state should be introduced before running multiple backend replicas.

## 7. Security Design

- Credentials are loaded from environment variables or `my_agent/.env`.
- Telegram webhooks can be protected with `TELEGRAM_WEBHOOK_SECRET`.
- User messages are treated as untrusted input.
- API keys and tokens must not be logged or committed.

See [SECURITY.md](./SECURITY.md) for operational security guidance.

## 8. Key Design Decisions

- Use a coordinator/sub-agent model to separate workflow control, retrieval, and synthesis.
- Use FastAPI as the integration boundary for both direct API calls and Telegram webhooks.
- Use in-memory sessions for early development simplicity.
- Prefer Telegram webhook mode for deployed environments.
- Keep search models Gemini-compatible because ADK `google_search` depends on Gemini support.

## 9. Known Limitations

- Sessions are not durable.
- Multiple service replicas would not share conversation context.
- Search depends on general web search availability and quality.
- Direct PDF parsing is not implemented yet.

