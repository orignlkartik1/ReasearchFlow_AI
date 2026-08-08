# Design

## Product Goal

ResearchFlow AI is designed to reduce the manual effort of early literature exploration. The assistant should help users move from a seminal paper to a structured view of recent work, open gaps, and future research directions.

## Interaction Design

The primary interaction is conversational:

1. The user provides a paper title, citation, abstract, or research prompt.
2. The system identifies the paper context it can infer.
3. The system searches for recent citing or related work.
4. The system synthesizes future research directions.
5. The user can ask follow-up questions in the same session.

Telegram is optimized for quick access and lightweight follow-up. The HTTP API is optimized for integration and testing.

## Agent Design

The agent graph uses a coordinator pattern:

- The coordinator owns the user-facing workflow and final response.
- The web research sub-agent owns retrieval through Google Search.
- The future research sub-agent owns synthesis and ideation.

This keeps retrieval and synthesis separate, which makes prompts easier to maintain and lets each sub-agent evolve independently.

## Response Design

Responses should be structured, source-aware, and clear about uncertainty. The system should prefer:

- Headings for major sections.
- Grouping papers by publication year.
- Explicit counts for found papers.
- Short rationales for future research suggestions.
- Clear messages when evidence is missing or search results are limited.

## API Design

The `/chat` endpoint intentionally uses a minimal request contract:

```json
{
  "user_id": "string",
  "message": "string"
}
```

`user_id` doubles as the ADK session identifier. This keeps multi-turn context simple for current local and single-instance deployments.

## Configuration Design

Runtime configuration is environment-based. `my_agent/.env` is supported for local development through `python-dotenv`; production deployments should use environment variables or a secret manager.

Model fallback is configured through comma-separated ordered lists. The runner validates model support and credentials before execution so misconfiguration fails early.

## Current Tradeoffs

- In-memory sessions are simple but not durable.
- Telegram webhook mode is production-friendly, while polling remains available only for debugging.
- Search depends on general web results rather than direct scholarly database APIs.
- PDF parsing is not yet implemented even though it is part of the product direction.

## Future Design Direction

- Add persistent sessions and user preferences.
- Add PDF/document ingestion.
- Add structured result export.
- Add citation graph exploration.
- Add a web dashboard for saved research projects.
