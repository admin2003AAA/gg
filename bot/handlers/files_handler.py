"""
/files command handler — lists indexed files with pagination.
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.services.index_service import IndexService
from bot.utils.helpers import split_msg

_svc = IndexService()
_ICONS = {
    "txt": "📄", "log": "📋", "md": "📝", "markdown": "📝", "rst": "📝",
    "json": "🔷", "jsonl": "🔷", "csv": "📊", "tsv": "📊",
    "xml": "🗂️", "yaml": "⚙️", "yml": "⚙️",
    "sqlite": "🗄️", "db": "🗄️", "sqlite3": "🗄️",
    "pdf": "📕", "docx": "📝", "xlsx": "📊", "xls": "📊",
}


async def cmd_files(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    files = await _svc.list_files()
    if not files:
        await update.message.reply_text(
            "📂 No files indexed yet.\n\nUse /scan to index the data directory."
        )
        return

    lines = [f"📁 **Indexed files ({len(files)}):**\n"]
    for f in files:
        ftype = f.get("file_type", "?")
        icon = _ICONS.get(ftype, "📄")
        size = _human_size(f.get("file_size") or 0)
        recs = f.get("record_count") or 0
        fid = f["id"]
        lines.append(
            f"{icon} `[{fid}]` **{f['filename']}**\n"
            f"   {recs:,} records · {size} · /summary_{fid}"
        )

    for part in split_msg("\n".join(lines)):
        await update.message.reply_text(part, parse_mode="Markdown")


def _human_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def register(app) -> None:
    app.add_handler(CommandHandler("files", cmd_files))
