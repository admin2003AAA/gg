"""
/search <query> handler — full-text search across indexed files.
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.services.search_service import SearchService
from bot.database.manager import DatabaseManager
from bot.config import DB_PATH, MAX_RESULTS_PER_SEARCH
from bot.utils.helpers import split_msg
from bot.utils.validators import clean

_svc = SearchService()
_db = DatabaseManager(DB_PATH)


async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    args = ctx.args or []
    query = clean(" ".join(args).strip())

    if not query or len(query) < 2:
        await update.message.reply_text(
            "🔍 Usage: `/search <query>`\n\nExample: `/search invoice`",
            parse_mode="Markdown",
        )
        return

    msg = await update.message.reply_text(
        f"🔍 Searching for `{query}`…", parse_mode="Markdown"
    )

    try:
        results, total, elapsed_ms = await _svc.search(query, limit=MAX_RESULTS_PER_SEARCH)
        await _db.init()
        await _db.increment_search(uid)
    except Exception as exc:
        await msg.edit_text(f"❌ Search failed: {exc}")
        return

    if not results:
        await msg.edit_text(
            f"🔍 No results found for `{query}`.\n\nTry different keywords.",
            parse_mode="Markdown",
        )
        return

    lines = [
        f"🔍 **Results for** `{query}`",
        f"📊 {total:,} match(es) · {elapsed_ms}ms\n",
    ]
    for i, r in enumerate(results, 1):
        ftype = r.get("file_type", "?").upper()
        snippet = (r.get("snippet") or "").strip()
        entry = (
            f"**{i}.** 📄 `{r['filename']}` [{ftype}]\n"
            f"   📊 {r.get('record_count', 0):,} records"
            + (f"\n   _{snippet}_" if snippet else "")
            + f"\n   👉 /summary\\_{r['id']}"
        )
        lines.append(entry)

    full_text = "\n".join(lines)
    parts = split_msg(full_text)
    await msg.edit_text(parts[0], parse_mode="Markdown")
    for part in parts[1:]:
        await update.message.reply_text(part, parse_mode="Markdown")


def register(app) -> None:
    app.add_handler(CommandHandler("search", cmd_search))
