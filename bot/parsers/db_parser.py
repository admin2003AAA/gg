"""
Database-family parsers: SQLite / .db / .sqlite3.
Extracts schema, table summaries — no arbitrary code execution.
"""
from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from .base import BaseParser, ParseResult

_SAMPLE_ROWS = 3
_MAX_TABLES = 50


class SqliteParser(BaseParser):
    SUPPORTED_EXTENSIONS = (".sqlite", ".db", ".sqlite3", ".s3db", ".sl3")
    PARSER_NAME = "sqlite"

    async def parse(self, path: Path) -> ParseResult:
        result = self._base_result(path)
        loop = asyncio.get_event_loop()
        try:
            tables, meta, search = await loop.run_in_executor(
                None, _inspect_sqlite, path
            )
            total_rows = sum(t.get("row_count", 0) for t in tables)
            result.tables = tables
            result.metadata = meta
            result.record_count = total_rows
            result.search_text = search
            result.content_preview = _build_preview(tables)[:2_000]
            result.summary = (
                f"🗄️ SQLite database · {len(tables)} table(s) · "
                f"{total_rows:,} total rows"
            )
        except Exception as exc:
            result.success = False
            result.error = str(exc)
        return result


def _inspect_sqlite(path: Path) -> tuple:
    """Open the DB read-only and introspect its schema."""
    uri = f"file:{path}?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    tables: List[Dict[str, Any]] = []
    search_parts: List[str] = []

    try:
        cur = con.cursor()
        cur.execute(
            "SELECT name, type FROM sqlite_master "
            "WHERE type IN ('table','view') ORDER BY name"
        )
        objects = cur.fetchall()[:_MAX_TABLES]

        for obj in objects:
            tname = obj["name"]
            ttype = obj["type"]
            # columns
            try:
                cur.execute(f"PRAGMA table_info({_quote(tname)})")  # noqa: S608
                cols_info = cur.fetchall()
                columns = [
                    {"name": c["name"], "type": c["type"], "pk": bool(c["pk"])}
                    for c in cols_info
                ]
                col_names = [c["name"] for c in columns]
            except Exception:
                columns = []
                col_names = []

            # row count (views may be slow)
            row_count = 0
            if ttype == "table":
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {_quote(tname)}")  # noqa: S608
                    row_count = cur.fetchone()[0]
                except Exception:
                    row_count = -1

            # sample rows (safe — no user input, read-only connection)
            preview: List[Dict] = []
            try:
                cur.execute(f"SELECT * FROM {_quote(tname)} LIMIT {_SAMPLE_ROWS}")  # noqa: S608
                for row in cur.fetchall():
                    preview.append(dict(row))
            except Exception:
                pass

            entry: Dict[str, Any] = {
                "name": tname,
                "type": ttype,
                "columns": columns,
                "column_names": col_names,
                "row_count": row_count,
                "preview": preview,
            }
            tables.append(entry)
            search_parts.append(tname)
            search_parts.extend(col_names)

        # SQLite version & page info
        cur.execute("PRAGMA page_count")
        page_count = cur.fetchone()[0]
        cur.execute("PRAGMA page_size")
        page_size = cur.fetchone()[0]

        meta: Dict[str, Any] = {
            "table_count": len([t for t in tables if t["type"] == "table"]),
            "view_count": len([t for t in tables if t["type"] == "view"]),
            "db_size_bytes": page_count * page_size,
            "table_names": [t["name"] for t in tables],
        }
    finally:
        con.close()

    return tables, meta, " ".join(search_parts)


def _quote(name: str) -> str:
    """Double-quote an identifier to prevent injection."""
    return '"' + name.replace('"', '""') + '"'


def _build_preview(tables: List[Dict]) -> str:
    lines = []
    for t in tables[:10]:
        cols = ", ".join(c["name"] for c in t.get("columns", [])[:10])
        lines.append(f"[{t['name']}] ({t.get('row_count', '?')} rows) — {cols}")
    return "\n".join(lines)
