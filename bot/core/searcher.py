"""
🔍 Searcher - wrapper around DatabaseManager.search
"""
from __future__ import annotations

from bot.config import DB_PATH, MAX_RESULTS
from bot.database.manager import DatabaseManager

_db = DatabaseManager(DB_PATH)


async def search_records(
    query: str,
    limit: int = MAX_RESULTS,
    offset: int = 0,
) -> list[dict]:
    await _db.init()
    return await _db.search(query, limit=limit, offset=offset)


async def total_count() -> int:
    await _db.init()
    return await _db.count_records()
