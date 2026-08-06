# ResearchFlow AI

ResearchFlow AI is a multi-agent academic research assistant built around Google ADK agents with a FastAPI backend and Telegram bot interface. It helps researchers analyze seminal academic papers, find recent citing papers, identify research trends, and discover promising future research areas.

**Live deployment:** Telegram bot @acadmeiabot (production backend hosted on Render).

**For detailed project specifications and requirements, see the [SRS Document](./SRS.md).**

## Project Overview

The project currently focuses on an integrated research workflow:

1. Collect or analyze a seminal paper
2. Extract its core context, references, keywords, and innovations
3. Search for recent citing papers (current year and previous year)
4. Synthesize gaps, trends, and promising future research areas
5. Deliver results through the Telegram bot (@acadmeiabot) or direct API access

## Project Structure

```text
ResearchFlow_AI/
+-- my_agent/
|   +-- __init__.py
|   +-- agent.py                          # Coordinator agent definition
|   +-- prompt.py                         # Coordinator prompt
|   +-- env.py                            # Environment variable handling
|   +-- backend/
|   |   +-- main.py                       # FastAPI application
|   |   +-- adk_runner.py                 # ADK agent runner & session management
|   |   +-- telegram.py                   # Telegram bot handler (entry point)
|   +-- sub_agents/
|       +-- academic_webresearch/
|       |   +-- agent.py                  # Web search sub-agent
|       |   +-- prompt.py                 # Web search prompt
|       +-- academic_newresearch/
|           +-- agent.py                  # Future research sub-agent
|           +-- prompt.py                 # Future research prompt
+-- SRS.md                                # Detailed specifications
+-- README.md                             # This file
+-- pyproject.toml                        # Project metadata and dependencies
+-- uv.lock                               # Dependency lock file
```

## Main Components

### Academic Coordinator Agent

`my_agent/agent.py` defines the root `academic_coordinator` agent using Google ADK.

The coordinator is responsible for managing the complete research workflow. It uses `gemini-2.5-flash` as the LLM (configurable via env) and orchestrates sub-agents through the `AgentTool` wrapper. The coordinator:

- Analyzes the seminal paper from user input
- Invokes the web research sub-agent to find citing papers
- Invokes the new research sub-agent to generate future directions
- Compiles and presents findings to the user
- Maintains conversation context for multi-turn interactions

The exported `root_agent` points to this coordinator:

```python
root_agent = Agent(
    name="academic_coordinator",
    model=MODEL,
    description="Analyzes seminal papers...",
    instruction=prompt.ACADEMIC_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=academic_websearch_agent),
        AgentTool(agent=academic_newresearch_agent),
    ],
)
```

### Coordinator Prompt

`my_agent/prompt.py` contains `ACADEMIC_COORDINATOR_PROMPT` which drives the end-to-end interaction flow with sub-agents and output formatting.

### Academic Web Research Sub-Agent

`my_agent/sub_agents/academic_webresearch/` contains the `academic_websearch_agent`. This agent uses the configured web search tool to find recent papers that cite the provided seminal paper and filters results for relevance.

### Academic New Research Sub-Agent

`my_agent/sub_agents/academic_newresearch/` contains the `academic_newresearch_agent`. This agent takes the seminal paper context and the recent citing papers, then synthesizes recommended future research areas.

### FastAPI Backend

`my_agent/backend/main.py` contains the FastAPI application with a `/chat` endpoint.

- Accepts POST requests with `user_id` and `message`
- Routes requests to the ADK runner for agent processing
- Returns JSON response with agent findings
- Handles concurrent user requests asynchronously
- Manages session creation and context preservation

### Telegram Bot Entry Point

`my_agent/backend/telegram.py` contains the Telegram bot entry point and handlers. The production Telegram bot is published as @acadmeiabot.

- Registers `/start` command with greeting
- Handles text messages and forwards them to the FastAPI backend via HTTP
- Uses async `httpx.AsyncClient` for non-blocking requests
- Displays agent responses back to the user
- Supports multi-turn conversations with context persistence

## Requirements

The project metadata is defined in `pyproject.toml`.

Current declared requirements:

- Python `>=3.14`
- `aiogram>=3.29.0` (alternative bot framework option)
- `fastapi>=0.139.0`
- `google-adk==2.3.0`
- `httpx>=0.28.1` (async HTTP client)
- `python-dotenv>=1.2.2`
- `python-telegram-bot>=22.8`
- `uvicorn>=0.51.0`

The source code imports Google ADK modules such as:

- `google.adk.agents`
- `google.adk.tools`
- `google.adk.runners`
- `google.adk.sessions`
- `google.genai.types`

Make sure the Google ADK package required by your environment is installed.

## Setup

This project includes a `uv.lock` file, so `uv` is the intended package manager.

```bash
uv sync
```

If you are not using `uv`, create a virtual environment and install the dependencies from `pyproject.toml` with your preferred Python package manager.

### Environment Variables

You need to configure the following environment variables. Create a `.env` file in the `my_agent/` directory:

```text
# Required for Google ADK agents
GOOGLE_API_KEY=your_google_adk_api_key

# Required for Telegram bot
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_USERNAME=acadmeiabot

# Optional backend configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
```

#### Advanced LLM Configuration (Optional)

For advanced model fallback and custom provider configuration:

```text
LLM_MODEL=gemini-2.5-flash
LLM_MODEL_FALLBACKS=openai/gpt-4.1,anthropic/claude-sonnet-4-5,groq/llama-3.3-70b-versatile
SEARCH_MODEL=gemini-2.5-flash
SEARCH_MODEL_FALLBACKS=gemini-3.5-flash-lite
```

Google ADK, Gemini, and LiteLLM providers require provider-specific credentials depending on the models you configure. Add only the keys for the providers you use:

- Google: `GOOGLE_API_KEY`
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Groq: `GROQ_API_KEY`

The agent validates every configured model at startup. During a run, ResearchFlow AI automatically retries with the next configured model when the active provider returns transient demand errors.

## Running (Development)

### Run FastAPI Backend

```bash
python -m uvicorn my_agent.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will start on `http://127.0.0.1:8000/` with the `/chat` endpoint available.

To test the backend:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "message": "Analyze the paper on Transformers"}'
```

### Run Telegram Bot (Development)

```bash
python -m my_agent.backend.telegram
```

The bot will connect to Telegram and start polling for messages. It will forward messages to the backend at `http://127.0.0.1:8000/chat`.

**Production note:** The published Telegram bot username is @acadmeiabot. Ensure the TELEGRAM_TOKEN you supply corresponds to that bot when deploying to production.

### Run With Google ADK CLI (Alternative)

The root agent is exposed as `root_agent` in `my_agent/agent.py`, which is the common structure expected by ADK tooling.

Depending on your installed ADK CLI and configuration, run the agent from the project root:

```bash
adk run --agent my_agent.agent:root_agent
```

## Workflow

The intended ResearchFlow AI workflow is:

1. User sends a message to Telegram bot (e.g., paper title or query)
2. Telegram bot forwards the message to FastAPI backend via HTTP POST to `/chat`
3. Backend creates a session for the user (if new) and calls the ADK runner
4. Coordinator agent analyzes the seminal paper for context
5. Coordinator calls `academic_websearch_agent` via AgentTool
6. Web research agent searches for recent citing papers using configured search tool
7. Coordinator calls `academic_newresearch_agent` via AgentTool
8. New research agent generates future research directions
9. Coordinator compiles findings and returns response to backend
10. Backend returns JSON response to Telegram bot
11. Telegram bot displays the research findings to the user
12. User can ask follow-up questions, and the session maintains context

## API Documentation

### POST /chat

Processes user research queries through the ADK agent system.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "user_id": "unique_user_identifier",
  "message": "User's research query or follow-up question"
}
```

**Response (Success - 200):**
```json
{
  "response": "Agent's research findings and analysis"
}
```

**Response (Error - 400/500):**
```json
{
  "detail": "Error message describing the issue"
}
```

## Contributing

We welcome contributions! See the SRS.md for detailed specifications. When contributing, ensure environment variables and bot credentials are not committed.

## Future Enhancements

ResearchFlow AI is actively evolving. Key planned improvements include:

- Full Telegram integration improvements and webhook support for production
- Advanced AI agents and memory systems
- Database backend for session persistence
- Citation network visualization and web dashboard

## Notes

- The production Telegram bot is published as @acadmeiabot.
- Sessions are stored in-memory by default and do not persist across server restarts (future: database backend).

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

For more information about Google ADK and Telegram Bot API, refer to:
- [Google ADK Documentation](https://ai.google.dev/)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
