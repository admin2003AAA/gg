"""
Async SQLite database manager for the file indexer bot.
All operations use aiosqlite for non-blocking I/O.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite
from loguru import logger

_MAX_SEARCH_TEXT_LEN = 500_000  # characters stored per file in FTS index


_DDL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS indexed_files (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    filename      TEXT    NOT NULL,
    filepath      TEXT    NOT NULL UNIQUE,
    file_type     TEXT    NOT NULL,
    file_size     INTEGER DEFAULT 0,
    record_count  INTEGER DEFAULT 0,
    char_count    INTEGER DEFAULT 0,
    indexed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status        TEXT    DEFAULT 'active',
    error_message TEXT,
    summary       TEXT,
    metadata_json TEXT,
    tables_json   TEXT
);

-- Standalone FTS5 table (simpler and reliable — stores its own content)
CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
    filename,
    search_text,
    file_id UNINDEXED,
    tokenize = 'unicode61 remove_diacritics 1'
);

CREATE TABLE IF NOT EXISTS users (
    telegram_id   INTEGER PRIMARY KEY,
    username      TEXT,
    joined_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    search_count  INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_files_type   ON indexed_files(file_type);
CREATE INDEX IF NOT EXISTS idx_files_status ON indexed_files(status);
"""


class DatabaseManager:
    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._db_path_str = str(db_path)
        self._ready = False

    async def init(self) -> None:
        if self._ready:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._db_path_str) as db:
            await db.executescript(_DDL)
            await db.commit()
        self._ready = True
        logger.info(f"📂 Database initialised: {self._path}")

    # ─── Files ───────────────────────────────────────────────────────────────

    async def upsert_file(
        self,
        filepath: str,
        filename: str,
        file_type: str,
        file_size: int,
        record_count: int,
        char_count: int,
        summary: str,
        metadata: Dict[str, Any],
        tables: List[Dict[str, Any]],
        search_text: str,
        content_preview: str,
        status: str = "active",
        error_message: Optional[str] = None,
    ) -> int:
        """Insert or replace a file record. Returns the file id."""
        async with aiosqlite.connect(self._db_path_str) as db:
            # Remove old FTS entry first
            old_cur = await db.execute(
                "SELECT id FROM indexed_files WHERE filepath = ?", (filepath,)
            )
            old_row = await old_cur.fetchone()
            if old_row:
                old_id = old_row[0]
                await db.execute(
                    "DELETE FROM content_fts WHERE file_id = ?", (old_id,)
                )
                await db.execute(
                    "DELETE FROM indexed_files WHERE id = ?", (old_id,)
                )

            cursor = await db.execute(
                """
                INSERT INTO indexed_files
                    (filename, filepath, file_type, file_size, record_count,
                     char_count, summary, metadata_json, tables_json, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    filename, filepath, file_type, file_size, record_count,
                    char_count, summary,
                    json.dumps(metadata, ensure_ascii=False, default=str),
                    json.dumps(tables, ensure_ascii=False, default=str),
                    status, error_message,
                ),
            )
            file_id = cursor.lastrowid

            # Insert into FTS
            await db.execute(
                "INSERT INTO content_fts (filename, search_text, file_id) VALUES (?, ?, ?)",
                (filename, search_text[:_MAX_SEARCH_TEXT_LEN], file_id),
            )
            await db.commit()
        return file_id

    async def mark_file_error(self, filepath: str, error: str) -> None:
        async with aiosqlite.connect(self._db_path_str) as db:
            await db.execute(
                "UPDATE indexed_files SET status='error', error_message=? WHERE filepath=?",
                (error[:1000], filepath),
            )
            await db.commit()

    async def get_all_files(self, status: str = "active") -> List[Dict]:
        async with aiosqlite.connect(self._db_path_str) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM indexed_files WHERE status=? ORDER BY indexed_at DESC",
                (status,),
            )
            rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def get_file_by_id(self, file_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self._db_path_str) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM indexed_files WHERE id=?", (file_id,)
            )
            row = await cursor.fetchone()
        return dict(row) if row else None

    # ─── Search ──────────────────────────────────────────────────────────────

    async def search_files(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[List[Dict], int]:
        """Full-text search across indexed content. Returns (results, total)."""
        # Sanitise: wrap in double-quotes for phrase matching, escape internal quotes
        safe_q = '"' + query.replace('"', '""') + '"'
        async with aiosqlite.connect(self._db_path_str) as db:
            db.row_factory = aiosqlite.Row

            # Total count
            count_cur = await db.execute(
                "SELECT COUNT(*) FROM content_fts WHERE content_fts MATCH ?",
                (safe_q,),
            )
            total = (await count_cur.fetchone())[0]

            # Fetch results joined to metadata
            cur = await db.execute(
                """
                SELECT
                    f.id, f.filename, f.file_type, f.file_size,
                    f.record_count, f.indexed_at, f.summary,
                    snippet(content_fts, 1, '**', '**', '…', 20) AS snippet
                FROM content_fts
                JOIN indexed_files f ON f.id = content_fts.file_id
                WHERE content_fts MATCH ?
                  AND f.status = 'active'
                ORDER BY rank
                LIMIT ? OFFSET ?
                """,
                (safe_q, limit, offset),
            )
            rows = await cur.fetchall()
        return [dict(r) for r in rows], total

    # ─── Stats ───────────────────────────────────────────────────────────────

    async def get_stats(self) -> Dict[str, Any]:
        async with aiosqlite.connect(self._db_path_str) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT
                    COUNT(*) AS total_files,
                    COALESCE(SUM(record_count), 0) AS total_records,
                    COALESCE(SUM(file_size), 0) AS total_size,
                    SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) AS active_files,
                    SUM(CASE WHEN status='error'  THEN 1 ELSE 0 END) AS error_files
                FROM indexed_files
                """
            )
            row = await cur.fetchone()
            stats = dict(row)
            # Per-type breakdown
            cur2 = await db.execute(
                """
                SELECT file_type, COUNT(*) as cnt, SUM(record_count) as recs
                FROM indexed_files WHERE status='active'
                GROUP BY file_type ORDER BY cnt DESC
                """
            )
            type_rows = await cur2.fetchall()
            stats["by_type"] = [dict(r) for r in type_rows]
        return stats

    # ─── Users ───────────────────────────────────────────────────────────────

    async def upsert_user(self, telegram_id: int, username: str = "") -> None:
        async with aiosqlite.connect(self._db_path_str) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_id, username)
                VALUES (?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    username = excluded.username,
                    last_active = CURRENT_TIMESTAMP
                """,
                (telegram_id, username),
            )
            await db.commit()

    async def increment_search(self, telegram_id: int) -> None:
        async with aiosqlite.connect(self._db_path_str) as db:
            await db.execute(
                "UPDATE users SET search_count = search_count + 1 WHERE telegram_id = ?",
                (telegram_id,),
            )
            await db.commit()

    async def count_users(self) -> int:
        async with aiosqlite.connect(self._db_path_str) as db:
            cur = await db.execute("SELECT COUNT(*) FROM users")
            row = await cur.fetchone()
        return row[0] if row else 0
