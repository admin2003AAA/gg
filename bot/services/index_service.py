"""
IndexService — high-level façade over the core indexer.
"""
from __future__ import annotations

from bot.core.indexer import index_file, scan_data_dir
from bot.database.manager import DatabaseManager
from bot.config import DB_PATH

_db = DatabaseManager(DB_PATH)


class IndexService:
    async def scan(self) -> dict:
        """Scan the data directory and index all supported files."""
        return await scan_data_dir()

    async def index_single(self, filepath: str) -> int:
        """Index a single file by path."""
        return await index_file(filepath)

    async def list_files(self) -> list:
        await _db.init()
        return await _db.get_all_files()

    async def get_file(self, file_id: int) -> dict | None:
        await _db.init()
        return await _db.get_file_by_id(file_id)
