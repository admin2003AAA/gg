"""
✅ التحقق من صحة البيانات - Validators
"""

import re
from pathlib import Path
from bot.config import SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_BYTES


def valid_query(q: str) -> bool:
    return bool(q and q.strip() and len(q.strip()) >= 2)


def valid_file(name: str) -> bool:
    return Path(name).suffix.lower() in SUPPORTED_EXTENSIONS


def valid_size(size: int) -> bool:
    return 0 < size <= MAX_FILE_SIZE_BYTES


def clean(q: str) -> str:
    """تنظيف وتعقيم نص البحث"""
    return re.sub(r'["\'\`;\\<>]', " ", q).strip()[:200]
