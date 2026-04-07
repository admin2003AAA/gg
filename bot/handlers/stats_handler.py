"""
/stats command handler — shows indexing and usage statistics.
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.services.summary_service import SummaryService
from bot.database.manager import DatabaseManager
from bot.config import DB_PATH
from bot.parsers.registry import registry

_svc = SummaryService()
_db = DatabaseManager(DB_PATH)


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await _db.init()
    stats = await _svc.get_stats()
    users = await _db.count_users()

    ext_list = "  ".join(f"`{e}`" for e in registry.supported_extensions())

    lines = [
        "📊 **Bot Statistics**",
        "━" * 28,
        f"📁 Total files   : **{stats.get('total_files', 0):,}**",
        f"✅ Active files   : **{stats.get('active_files', 0):,}**",
        f"❌ Error files    : **{stats.get('error_files', 0):,}**",
        f"📋 Total records  : **{stats.get('total_records') or 0:,}**",
        f"💾 Total size     : **{_human_size(stats.get('total_size') or 0)}**",
        f"👥 Total users    : **{users:,}**",
        "",
        "📑 **By file type:**",
    ]
    for row in (stats.get("by_type") or []):
        lines.append(
            f"  • `{row['file_type'].upper():<8}` {row['cnt']} file(s)"
            + (f" · {row['recs']:,} records" if row.get("recs") else "")
        )

    lines += [
        "",
        "🔌 **Supported formats:**",
        ext_list,
    ]

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f} TB"


def register(app) -> None:
    app.add_handler(CommandHandler("stats", cmd_stats))
