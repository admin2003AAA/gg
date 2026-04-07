"""
SearchService — wraps database full-text search with caching.
"""
from __future__ import annotations

import time
from typing import Dict, List, Tuple

from cachetools import TTLCache
from loguru import logger

from bot.database.manager import DatabaseManager
from bot.config import DB_PATH, MAX_RESULTS_PER_SEARCH, CACHE_SIZE

_db = DatabaseManager(DB_PATH)
_cache: TTLCache = TTLCache(maxsize=CACHE_SIZE, ttl=300)


class SearchService:
    async def search(
        self,
        query: str,
        limit: int = MAX_RESULTS_PER_SEARCH,
        offset: int = 0,
    ) -> Tuple[List[Dict], int, int]:
        """
        Full-text search across indexed files.
        Returns (results, total_count, elapsed_ms).
        """
        cache_key = f"{query}:{limit}:{offset}"
        if cache_key in _cache:
            return _cache[cache_key]

        await _db.init()
        t0 = time.perf_counter()
        try:
            results, total = await _db.search_files(query, limit=limit, offset=offset)
        except Exception as exc:
            logger.error(f"Search error: {exc}")
            results, total = [], 0
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        value = (results, total, elapsed_ms)
        _cache[cache_key] = value
        return value

    def clear_cache(self) -> None:
        _cache.clear()
