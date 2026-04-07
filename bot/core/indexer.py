"""
Core file indexer — orchestrates parsers and persists results.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Coroutine, Optional

from loguru import logger

from bot.config import DATA_DIR, DB_PATH
from bot.parsers.registry import registry
from bot.database.manager import DatabaseManager

_db = DatabaseManager(DB_PATH)

ProgressCb = Optional[Callable[[str, int, int], Coroutine]]


async def ensure_db() -> None:
    await _db.init()


async def index_file(
    filepath: str,
    progress_cb: ProgressCb = None,
) -> int:
    """
    Parse *filepath* and store the result in the index DB.
    Returns the number of records indexed.
    """
    path = Path(filepath)
    await ensure_db()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    logger.info(f"🔍 Indexing: {path.name}")
    t0 = time.perf_counter()

    result = await registry.parse(path)

    elapsed = time.perf_counter() - t0

    if not result.success:
        await _db.mark_file_error(filepath, result.error)
        logger.warning(f"⚠️ Parse error for {path.name}: {result.error}")
        raise RuntimeError(result.error)

    file_id = await _db.upsert_file(
        filepath=str(path.resolve()),
        filename=path.name,
        file_type=result.file_type,
        file_size=result.file_size,
        record_count=result.record_count,
        char_count=result.char_count,
        summary=result.summary,
        metadata=result.metadata,
        tables=result.tables,
        search_text=result.search_text,
        content_preview=result.content_preview,
    )

    if progress_cb:
        await progress_cb(path.name, result.record_count, file_id)

    logger.success(
        f"✅ Indexed {path.name}: {result.record_count:,} records in {elapsed:.2f}s"
    )
    return result.record_count


async def scan_data_dir() -> dict:
    """
    Scan DATA_DIR, index all supported files, return a summary dict.
    """
    await ensure_db()
    extensions = set(registry.supported_extensions())
    files = [
        p for p in DATA_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in extensions
    ]

    total_files = len(files)
    indexed = 0
    failed = 0
    total_records = 0

    for f in files:
        try:
            n = await index_file(str(f))
            total_records += n
            indexed += 1
        except Exception as exc:
            logger.error(f"❌ Failed to index {f.name}: {exc}")
            failed += 1

    return {
        "found": total_files,
        "indexed": indexed,
        "failed": failed,
        "total_records": total_records,
    }
