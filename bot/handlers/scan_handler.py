"""
/scan command handler — triggers indexing of the data directory.
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config import ADMIN_IDS
from bot.services.index_service import IndexService

_svc = IndexService()


async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Admin only.")
        return

    msg = await update.message.reply_text("🔄 Scanning data directory…")
    try:
        result = await _svc.scan()
        text = (
            f"✅ **Scan complete!**\n\n"
            f"📁 Files found : {result['found']}\n"
            f"✅ Indexed      : {result['indexed']}\n"
            f"❌ Failed       : {result['failed']}\n"
            f"📊 Total records: {result['total_records']:,}"
        )
    except Exception as exc:
        text = f"❌ Scan failed: {exc}"

    await msg.edit_text(text, parse_mode="Markdown")


def register(app) -> None:
    app.add_handler(CommandHandler("scan", cmd_scan))
