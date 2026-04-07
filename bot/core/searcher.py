"""
🔍 Searcher — thin wrapper kept for backward compatibility.
New code should use SearchService directly.
"""
from __future__ import annotations

from bot.config import DB_PATH, MAX_RESULTS_PER_SEARCH
from bot.database.manager import DatabaseManager

_db = DatabaseManager(DB_PATH)


async def search_records(
    query: str,
    limit: int = MAX_RESULTS_PER_SEARCH,
    offset: int = 0,
) -> list[dict]:
    await _db.init()
    results, _ = await _db.search_files(query, limit=limit, offset=offset)
    return results


async def total_count() -> int:
    await _db.init()
    stats = await _db.get_stats()
    return stats.get("total_records", 0)
