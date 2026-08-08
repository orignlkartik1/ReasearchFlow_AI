import hmac
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from my_agent.backend.adk_runner import ask_agent
from my_agent.backend.telegram import (
    process_telegram_update,
    set_telegram_webhook,
    telegram_app,
)
from my_agent.env import load_environment

load_environment()
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
TELEGRAM_WEBHOOK_URL = os.environ.get("TELEGRAM_WEBHOOK_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_app.initialize()
    await telegram_app.start()

    if TELEGRAM_WEBHOOK_URL:
        await set_telegram_webhook(
            TELEGRAM_WEBHOOK_URL,
            secret_token=TELEGRAM_WEBHOOK_SECRET,
        )

    try:
        yield
    finally:
        await telegram_app.stop()
        await telegram_app.shutdown()


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        response = await ask_agent(
            req.user_id,
            req.message,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "response": response
    }


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
):
    if TELEGRAM_WEBHOOK_SECRET and not hmac.compare_digest(
        x_telegram_bot_api_secret_token or "",
        TELEGRAM_WEBHOOK_SECRET,
    ):
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Telegram update payload") from exc

    background_tasks.add_task(process_telegram_update, payload)

    return {
        "ok": True
    }
