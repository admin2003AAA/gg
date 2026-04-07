"""
/start and /help handlers.
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config import ADMIN_IDS, DB_PATH
from bot.utils.helpers import kb_main, kb_admin
from bot.database.manager import DatabaseManager

_db = DatabaseManager(DB_PATH)

_HELP_TEXT = (
    "📖 *File Indexer Bot — Help*\n\n"
    "*Commands:*\n"
    "• /scan — index all files in the data directory _(admin)_\n"
    "• /files — list all indexed files\n"
    "• /search `<query>` — full-text search\n"
    "• /summary `<id>` — detailed summary of a file\n"
    "• /stats — indexing & usage statistics\n\n"
    "*Upload a file* to automatically index it _(admin)_.\n\n"
    "*Supported formats:*\n"
    "`txt  log  md  json  csv  xml  yaml  sqlite  db  pdf  docx  xlsx`"
)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    uname = update.effective_user.username or ""
    await _db.init()
    await _db.upsert_user(uid, uname)

    is_admin = uid in ADMIN_IDS
    text = (
        "👋 *Welcome to File Indexer Bot!*\n\n"
        "I can index files from many formats and let you search their content.\n\n"
        "📂 Drop files here or use /scan to index the data directory.\n"
        "🔍 Use /search to find anything across all indexed files.\n\n"
        "_Type /help for the full command list._"
    )
    kb = kb_admin() if is_admin else kb_main()
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_HELP_TEXT, parse_mode="Markdown")


def register(app) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
