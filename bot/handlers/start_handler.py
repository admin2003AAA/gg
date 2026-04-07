"""
🚀 Start / Help handler
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config import ADMIN_IDS
from bot.utils.helpers import kb_main, kb_admin
from bot.database.manager import DatabaseManager
from bot.config import DB_PATH

_db = DatabaseManager(DB_PATH)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uname = update.effective_user.username or ""
    await _db.init()
    await _db.upsert_user(uid, uname)

    is_admin = uid in ADMIN_IDS
    text = (
        "👋 *مرحباً بك في بوت البيانات العراقية!*\n\n"
        "🔍 أرسل أي رقم هاتف أو اسم للبحث.\n"
        "📤 أرسل ملف Excel/CSV لرفعه وفهرسته.\n\n"
        "_البوت يعمل على مدار الساعة._"
    )
    kb = kb_admin() if is_admin else kb_main()
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *المساعدة*\n\n"
        "• ابعث اسماً أو رقم هاتف → سيبحث البوت تلقائياً.\n"
        "• أرسل ملف .xlsx أو .csv → يرفعه ويفهرسه.\n"
        "• /stats → إحصائيات قاعدة البيانات.\n"
        "• /admin → لوحة تحكم (للمشرفين).",
        parse_mode="Markdown",
    )


def register(app):
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
