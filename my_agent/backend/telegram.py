import logging
import os

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from my_agent.backend.adk_runner import ask_agent
from my_agent.backend.telegram_messages import (
    safe_delete_message,
    safe_edit_text,
    send_long_message,
)
from my_agent.env import require_env

BOT_TOKEN = require_env("TELEGRAM_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    await update.message.reply_text(
        "Welcome to ResearchFlow AI!\n\n"
        "I can help you analyze research papers, discover recent work, "
        "and suggest future research directions.\n\n"
        "Send me a message to begin."
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None or update.effective_chat is None:
        logger.info("Ignoring Telegram update without a text message")
        return

    user_id = str(update.effective_user.id)
    message = update.message.text

    if not message:
        logger.info("Ignoring Telegram message without text from %s", user_id)
        return

    logger.info("Message received from %s", user_id)

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    processing_msg = await update.message.reply_text(
        "Request received.\n\n"
        "ResearchFlow AI is analyzing your request.\n"
        "Please wait..."
    )

    try:
        reply = await ask_agent(user_id, message)
        if not reply:
            reply = "Sorry, I couldn't generate a response."

        logger.info("Generated response length: %d characters", len(reply))

        try:
            await safe_delete_message(processing_msg)
            await send_long_message(
                context.bot,
                update.effective_chat.id,
                reply,
            )
        except Exception:
            logger.exception("Failed while sending Telegram response")
            await update.message.reply_text("Failed to send the response.")

    except RuntimeError as exc:
        logger.exception("Agent error")
        await safe_edit_text(
            processing_msg.edit_text,
            "ResearchFlow AI could not complete the request.\n\n"
            f"{str(exc)}",
        )

    except Exception as exc:
        logger.exception("Unexpected error")
        await safe_edit_text(
            processing_msg.edit_text,
            "An unexpected error occurred.\n\n"
            f"{str(exc)}",
        )


def create_telegram_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    return application


telegram_app = create_telegram_application()


async def process_telegram_update(payload: dict) -> None:
    update = Update.de_json(payload, telegram_app.bot)
    if update is None:
        logger.info("Ignoring invalid Telegram update payload")
        return

    await telegram_app.process_update(update)


async def set_telegram_webhook(webhook_url: str, secret_token: str | None = None) -> None:
    await telegram_app.bot.set_webhook(
        url=webhook_url,
        secret_token=secret_token,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


async def delete_telegram_webhook() -> None:
    await telegram_app.bot.delete_webhook(drop_pending_updates=True)


if __name__ == "__main__":
    if os.environ.get("ENABLE_TELEGRAM_POLLING") != "1":
        raise RuntimeError(
            "Long polling is disabled. Run FastAPI and use /telegram/webhook instead. "
            "For temporary local debugging only, set ENABLE_TELEGRAM_POLLING=1."
        )

    logger.info("Starting ResearchFlow AI Telegram bot with temporary long polling")
    telegram_app.run_polling()
