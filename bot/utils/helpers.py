"""
🔧 دوال مساعدة - Helpers / Keyboards
"""

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ─────────────────────────────────────────────
# ⌨️  لوحات المفاتيح
# ─────────────────────────────────────────────

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 بحث سريع",  callback_data="menu:search"),
         InlineKeyboardButton("🎯 بحث متقدم", callback_data="menu:advanced")],
        [InlineKeyboardButton("📊 إحصائيات",  callback_data="menu:stats"),
         InlineKeyboardButton("📁 الملفات",   callback_data="menu:files")],
        [InlineKeyboardButton("❓ مساعدة",    callback_data="menu:help")],
    ])


def kb_search_type() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 بالاسم",     callback_data="stype:name"),
         InlineKeyboardButton("🪪 بالهوية",   callback_data="stype:id")],
        [InlineKeyboardButton("📞 بالهاتف",   callback_data="stype:phone"),
         InlineKeyboardButton("🏛️ بالمحافظة", callback_data="stype:province")],
        [InlineKeyboardButton("🎯 تقريبي",    callback_data="stype:fuzzy"),
         InlineKeyboardButton("🔬 مركب",      callback_data="stype:advanced")],
        [InlineKeyboardButton("❌ إلغاء",      callback_data="cancel")],
    ])


def kb_admin() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 فهرسة كل الملفات", callback_data="admin:index_all")],
        [InlineKeyboardButton("📤 رفع ملف",     callback_data="admin:upload"),
         InlineKeyboardButton("🔄 إعادة فهرسة", callback_data="admin:reindex")],
        [InlineKeyboardButton("👥 المستخدمون",  callback_data="admin:users"),
         InlineKeyboardButton("📋 السجلات",     callback_data="admin:logs")],
        [InlineKeyboardButton("🔧 صيانة",       callback_data="admin:maintenance"),
         InlineKeyboardButton("📢 إذاعة",       callback_data="admin:broadcast")],
        [InlineKeyboardButton("🗑️ مسح الكاش",  callback_data="admin:clear_cache"),
         InlineKeyboardButton("📊 إحصائيات",   callback_data="admin:stats")],
    ])


def kb_pagination(page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    row: list = []
    if page > 1:
        row.append(InlineKeyboardButton("◀️", callback_data=f"{prefix}:page:{page-1}"))
    row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        row.append(InlineKeyboardButton("▶️", callback_data=f"{prefix}:page:{page+1}"))
    return InlineKeyboardMarkup([row]) if row else InlineKeyboardMarkup([])


def kb_confirm(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ تأكيد",  callback_data=f"confirm:{action}"),
        InlineKeyboardButton("❌ إلغاء", callback_data="cancel"),
    ]])


def kb_cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
    ]])


# ─────────────────────────────────────────────
# 🔧 دوال مساعدة
# ─────────────────────────────────────────────

def split_msg(text: str, max_len: int = 4096) -> List[str]:
    if len(text) <= max_len:
        return [text]
    parts: List[str] = []
    while text:
        if len(text) <= max_len:
            parts.append(text)
            break
        cut = text.rfind("\n", 0, max_len)
        if cut == -1:
            cut = max_len
        parts.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return parts
