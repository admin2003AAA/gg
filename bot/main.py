"""
Bot entry point — builds the Application and registers all handlers.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from loguru import logger
from telegram.ext import Application

from bot.config import BOT_TOKEN, LOG_LEVEL, DB_PATH
from bot.database.manager import DatabaseManager
from bot.core.file_watcher import watcher

# ─── logging ─────────────────────────────────────────────────────────────────

logger.remove()
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
)
logger.add(
    Path(__file__).parent.parent / "logs" / "bot.log",
    level="DEBUG",
    rotation="10 MB",
    retention="14 days",
    compression="gz",
)


# ─── register handlers ───────────────────────────────────────────────────────

def _register_handlers(app: Application) -> None:
    from bot.handlers import (
        start_handler,
        upload_handler,
        scan_handler,
        files_handler,
        search_handler,
        summary_handler,
        stats_handler,
    )
    start_handler.register(app)
    upload_handler.register(app)
    scan_handler.register(app)
    files_handler.register(app)
    search_handler.register(app)
    summary_handler.register(app)
    stats_handler.register(app)


# ─── lifecycle ────────────────────────────────────────────────────────────────

async def post_init(app: Application) -> None:
    db = DatabaseManager(DB_PATH)
    await db.init()
    loop = asyncio.get_event_loop()
    watcher.start(loop)
    logger.success("🤖 Bot started and ready.")


async def post_shutdown(app: Application) -> None:
    watcher.stop()
    logger.info("🛑 Bot shut down.")


# ─── main ─────────────────────────────────────────────────────────────────────

async def main() -> None:
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is not set. Please configure it in .env")
        sys.exit(1)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    _register_handlers(app)

    logger.info("🚀 Starting bot…")
    await app.run_polling(drop_pending_updates=True)
