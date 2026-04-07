"""
📤 معالج رفع الملفات - Upload Handler
"""

from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from bot.config import DATA_DIR, SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_BYTES, ADMIN_IDS
from bot.core.indexer import index_file
from bot.utils.helpers import kb_admin


async def handle_upload(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tid = update.effective_user.id
    if tid not in ADMIN_IDS:
        return await update.message.reply_text("🚫 هذا الأمر للمشرفين فقط.")

    doc = update.message.document
    if not doc:
        return

    ext = Path(doc.file_name or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return await update.message.reply_text(
            f"⚠️ نوع الملف غير مدعوم.\n"
            f"الأنواع المدعومة: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    if doc.file_size and doc.file_size > MAX_FILE_SIZE_BYTES:
        mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        return await update.message.reply_text(f"⚠️ الملف أكبر من {mb}MB.")

    msg = await update.message.reply_text(f"⏳ جاري تنزيل **{doc.file_name}** …",
                                          parse_mode="Markdown")

    dest = DATA_DIR / doc.file_name
    file = await doc.get_file()
    await file.download_to_drive(str(dest))

    await msg.edit_text(f"📂 جاري فهرسة **{doc.file_name}** …", parse_mode="Markdown")

    progress_msgs: list = []

    async def progress(name: str, count: int, _fid: int):
        text = f"⚙️ {name}: {count:,} سجل حتى الآن …"
        if not progress_msgs:
            progress_msgs.append(await msg.edit_text(text))
        elif count % 5000 == 0:
            await progress_msgs[0].edit_text(text)

    try:
        total = await index_file(str(dest), progress_cb=progress)
        await msg.edit_text(
            f"✅ تمت الفهرسة!\n"
            f"📄 الملف: `{doc.file_name}`\n"
            f"📊 السجلات: `{total:,}`",
            parse_mode="Markdown",
            reply_markup=kb_admin(),
        )
    except Exception as e:
        await msg.edit_text(f"❌ فشلت الفهرسة: {e}")


def register(app):
    app.add_handler(
        MessageHandler(filters.Document.ALL, handle_upload)
    )
