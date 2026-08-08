# Software Requirements Specification

## ResearchFlow AI

**Document Version:** 4.0  
**Date:** 2026-08-08  
**Project:** ResearchFlow AI - Academic Research Assistant  
**Author:** orignlkartik1

## 1. Introduction

### 1.1 Purpose

ResearchFlow AI is a multi-agent assistant for academic literature exploration. It analyzes a seminal paper, discovers recent citing or related papers, and proposes future research directions through a conversational API and Telegram interface.

### 1.2 Scope

The system includes:

- Google ADK coordinator and sub-agent orchestration.
- FastAPI backend with a `/chat` endpoint.
- Telegram bot integration through webhook mode and optional local polling.
- In-memory conversation sessions.
- Model configuration and fallback support for reasoning and search agents.
- Environment-based configuration for credentials and runtime options.

### 1.3 Definitions

| Term | Definition |
|------|------------|
| ADK | Google Agent Development Kit |
| AgentTool | ADK wrapper that allows one agent to call another agent |
| Coordinator | Root agent that manages the complete workflow |
| Seminal paper | Foundational academic work used as the starting point |
| Session | Conversation context associated with a user ID |
| Webhook | HTTP endpoint used by Telegram to deliver bot updates |

## 2. Overall Description

### 2.1 Product Perspective

ResearchFlow AI is a Python service that combines:

1. A Google ADK agent graph.
2. A FastAPI HTTP application.
3. A Telegram bot interface.
4. External model, search, and Telegram APIs.

### 2.2 Product Functions

- Accept research requests through HTTP or Telegram.
- Extract useful context from a paper title, citation, abstract, or user-provided metadata.
- Search for recent papers that cite or extend the seminal work.
- Group recent papers by year and include source links where available.
- Generate at least 10 future research areas when enough input evidence exists.
- Preserve context for follow-up questions.
- Retry transient model/provider failures using configured fallback models.

### 2.3 User Classes

- Researchers exploring literature trends.
- Students preparing thesis or dissertation topics.
- Academics evaluating citation influence.
- API consumers integrating the research workflow into another application.
- Telegram users who prefer a chat interface.

### 2.4 Operating Environment

- Python `>=3.13`
- `uv` for dependency management
- FastAPI with Uvicorn
- Google ADK `2.3.0`
- python-telegram-bot `22.8+`
- Internet access for model, search, and Telegram APIs

### 2.5 Constraints

- Google Search tool support requires Gemini-compatible search models.
- Credentials must be provided through environment variables or `my_agent/.env`.
- In-memory sessions do not survive process restarts.
- PDF parsing is a planned capability; current implementation primarily accepts text and metadata input.

## 3. Functional Requirements

### 3.1 Paper Analysis

- **F1.1** The system shall accept paper titles, citations, abstracts, summaries, or paper metadata through user messages.
- **F1.2** The coordinator shall extract title, authors, publication year, abstract, summary, keywords, innovations, and references when available.
- **F1.3** The coordinator shall clearly state when required metadata cannot be determined from the provided input.
- **F1.4** The system should support direct PDF ingestion in a future release.

### 3.2 Web Research

- **F2.1** The web research sub-agent shall use the ADK Google Search tool.
- **F2.2** The sub-agent shall search for recent citing or related papers from the current year and previous year.
- **F2.3** The sub-agent shall target at least 10 distinct papers per year when available.
- **F2.4** Results shall include title, authors, year, source, and link when available.
- **F2.5** Results shall be deduplicated and grouped by year.

### 3.3 Future Research Synthesis

- **F3.1** The future research sub-agent shall analyze the seminal paper and recent paper collection.
- **F3.2** The sub-agent shall generate at least 10 distinct future research areas when input evidence is sufficient.
- **F3.3** Each area shall include a concise title and rationale.
- **F3.4** Suggestions shall balance practical utility, unexpectedness, and emerging popularity.
- **F3.5** Relevant authors may be listed when the source material supports that mapping.

### 3.4 API Backend

- **F4.1** The backend shall expose `POST /chat`.
- **F4.2** The request body shall include `user_id` and `message`.
- **F4.3** The backend shall create a session for a new user ID.
- **F4.4** The backend shall preserve context across requests for the same user ID while the process is running.
- **F4.5** The backend shall return JSON containing a `response` field.
- **F4.6** Runtime agent failures shall return a service error with a useful message.

### 3.5 Telegram Interface

- **F5.1** The bot shall respond to `/start`.
- **F5.2** The bot shall forward text messages to the agent workflow.
- **F5.3** The bot shall show a processing message while the agent runs.
- **F5.4** The bot shall split long responses to respect Telegram message limits.
- **F5.5** Very large responses may be delivered as text attachments.
- **F5.6** Webhook mode shall support optional secret token validation.
- **F5.7** Long polling shall be available only when explicitly enabled for local debugging.

### 3.6 Model Configuration

- **F6.1** The system shall support `LLM_MODEL` and `SEARCH_MODEL`.
- **F6.2** The system shall support ordered fallback lists through `LLM_MODEL_FALLBACKS` and `SEARCH_MODEL_FALLBACKS`.
- **F6.3** The system shall validate configured model names before executing an agent run.
- **F6.4** The system shall skip fallback models when required provider credentials are missing.
- **F6.5** The system shall retry only transient provider errors on fallback models.

## 4. Non-Functional Requirements

### 4.1 Performance

- **NF1.1** Simple API validation and session lookup should complete in under 2 seconds.
- **NF1.2** Agent response time depends on model and search latency; long-running research requests may exceed normal HTTP chat latency.
- **NF1.3** Telegram users shall receive immediate processing feedback.

### 4.2 Reliability

- **NF2.1** The backend shall handle malformed JSON and invalid webhook secrets.
- **NF2.2** Telegram send/edit/delete errors shall be logged without crashing the process.
- **NF2.3** Transient model failures shall use configured fallback attempts.

### 4.3 Security

- **NF3.1** Credentials shall not be committed to source control.
- **NF3.2** `.env` files shall be treated as local secrets.
- **NF3.3** Telegram webhook requests shall be protected with `TELEGRAM_WEBHOOK_SECRET` in deployed environments.
- **NF3.4** Error messages shall not include API keys, tokens, or secret values.
- **NF3.5** User input shall be treated as untrusted content.

### 4.4 Maintainability

- **NF4.1** Code shall follow clear Python module boundaries.
- **NF4.2** Agent prompts shall remain in prompt modules.
- **NF4.3** Backend route handlers shall delegate agent execution to `adk_runner.py`.
- **NF4.4** Documentation shall be updated with behavior-changing code changes.

## 5. Architecture

```text
Telegram User or API Client
        |
        v
FastAPI app: my_agent.backend.main
        |
        v
ADK runner: my_agent.backend.adk_runner
        |
        v
Coordinator agent: my_agent.agent
        |
        +--> Web research sub-agent + Google Search
        |
        +--> Future research sub-agent
        |
        v
Response returned to API client or Telegram user
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for implementation details.

## 6. Data Requirements

### 6.1 Input Data

- `user_id`
- User message text
- Paper title, DOI, abstract, citation, or metadata
- Optional conversation context from existing in-memory session

### 6.2 Output Data

- Paper summary and extracted metadata
- Recent citing or related papers
- Future research directions
- Error details for recoverable failures

### 6.3 Storage

- Runtime sessions: in-memory ADK session service
- Configuration: process environment and `my_agent/.env`
- Logs: application logger output
- Persistent storage: not currently implemented

## 7. Interface Requirements

### 7.1 Chat API

`POST /chat`

```json
{
  "user_id": "string",
  "message": "string"
}
```

Success response:

```json
{
  "response": "string"
}
```

### 7.2 Telegram Webhook

`POST /telegram/webhook`

- Accepts Telegram update JSON.
- Validates `X-Telegram-Bot-Api-Secret-Token` when a secret is configured.
- Schedules update processing in a background task.

## 8. Acceptance Criteria

- [ ] `/chat` accepts valid requests and returns a response.
- [ ] Sessions are reused for repeated `user_id` values.
- [ ] `/telegram/webhook` rejects invalid secrets when a secret is configured.
- [ ] The Telegram bot handles long responses without exceeding message limits.
- [ ] Model fallback configuration validates before execution.
- [ ] Missing credentials fail with actionable messages.
- [ ] README, SRS, architecture, design, security, contribution, code of conduct, and changelog documents are present.
- [ ] No real secrets are included in documentation or examples.

## 9. Future Enhancements

- Persistent session storage with PostgreSQL, MongoDB, or Redis.
- Direct PDF upload and parsing.
- Citation graph visualization.
- Web dashboard for saved research projects.
- Export to Markdown, PDF, JSON, and BibTeX.
- Authentication and per-user rate limiting for public deployments.
- Structured observability with metrics and tracing.

## 10. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-09 | orignlkartik1 | Initial SRS |
| 2.0 | 2026-07-12 | orignlkartik1 | Added backend, FastAPI, and session details |
| 3.0 | 2026-07-18 | orignlkartik1 | Expanded multi-turn and future enhancement requirements |
| 4.0 | 2026-08-08 | orignlkartik1 | Aligned requirements with current code, webhook mode, model fallback, and documentation set |
