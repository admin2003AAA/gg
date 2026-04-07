"""
/summary <id> and /summary_<id> shortcut handler.
"""
from __future__ import annotations

import re

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from bot.services.summary_service import SummaryService
from bot.utils.helpers import split_msg

_svc = SummaryService()


async def cmd_summary(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    args = ctx.args or []
    if not args:
        await update.message.reply_text(
            "📋 Usage: `/summary <file_id>`\n\nGet file IDs from /files.",
            parse_mode="Markdown",
        )
        return
    try:
        file_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ File ID must be a number.")
        return

    await _deliver_summary(update, file_id)


async def cmd_summary_inline(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /summary_<id> shortcut commands generated in file listings."""
    text = update.message.text or ""
    m = re.search(r"/summary_(\d+)", text)
    if not m:
        return
    file_id = int(m.group(1))
    await _deliver_summary(update, file_id)


async def _deliver_summary(update: Update, file_id: int) -> None:
    msg = await update.message.reply_text("⏳ Building summary…")
    summary = await _svc.get_summary(file_id)
    parts = split_msg(summary)
    await msg.edit_text(parts[0], parse_mode="Markdown")
    for part in parts[1:]:
        await update.message.reply_text(part, parse_mode="Markdown")


def register(app) -> None:
    app.add_handler(CommandHandler("summary", cmd_summary))
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r"^/summary_\d+"),
            cmd_summary_inline,
        )
    )
